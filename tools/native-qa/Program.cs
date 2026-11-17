using System.IO;
using CmlLib.Core;
using CmlLib.Core.Auth;
using CmlLib.Core.ProcessBuilder;
using Minecraft;

if (args.Length != 1)
    throw new ArgumentException("Pass the absolute QA run directory.");
var root = Path.GetFullPath(args[0]);
if (Path.GetFileName(Path.GetDirectoryName(root)) != "agent-runs" ||
    !File.Exists(Path.Combine(root, "RUN.json")))
    throw new IOException("Expected a marked local QA run.");
var paths = new AppPaths(root);
const string packName = "Better Vanilla";
var logger = new Logger(paths.LogFile);
using var runtimeService = new PackRuntimeService(paths, logger);
using var instanceService = new PackInstanceService(paths, logger);
using var timeout = new CancellationTokenSource(TimeSpan.FromMinutes(18));
var progress = new StageProgress();
var prepared = await runtimeService.PrepareAsync(packName, progress, timeout.Token);
var instance = await instanceService.PrepareAsync(packName, timeout.Token);
if (prepared.Descriptor.MinecraftVersion != "26.3" ||
    prepared.Descriptor.Loader.Type != PackLoaderKind.Fabric ||
    prepared.Descriptor.Loader.Version != "0.20.1")
    throw new IOException("Unexpected QA platform.");

var launcher = runtimeService.CreateLocalLauncher(prepared);
var profile = await launcher.GetVersionAsync(prepared.ProfileId, timeout.Token);
var shared = launcher.MinecraftPath;
var launchPath = new MinecraftPath(instance.GameDirectory)
{
    Library = shared.Library,
    Versions = shared.Versions,
    Assets = shared.Assets,
    Resource = shared.Resource,
    Runtime = shared.Runtime
};
launchPath.CreateDirs();
var home = Directory.CreateDirectory(Path.Combine(root, "qa-home")).FullName;
var session = MSession.CreateOfflineSession("BetterVanillaQA");
session.UUID = "f2cf86fc70524db3b414ff69f6ea8a81";
var options = new MLaunchOption
{
    Path = launchPath,
    JavaPath = prepared.JavaPath,
    Session = session,
    MaximumRamMb = 6144,
    MinimumRamMb = 1024,
    ScreenWidth = 1120,
    ScreenHeight = 630,
    GameLauncherName = "LANMinecraft",
    ExtraJvmArguments = [new MArgument("-Duser.home=" + home)]
};
using var client = launcher.BuildProcess(profile, options);
client.StartInfo.UseShellExecute = false;
client.Start();
Console.WriteLine($"QA_CLIENT_PID={client.Id}");
await client.WaitForExitAsync();
Console.WriteLine($"QA_CLIENT_EXIT={client.ExitCode}");
Environment.ExitCode = client.ExitCode;

sealed class StageProgress : IProgress<RuntimePreparationProgress>
{
    private RuntimePreparationStage? current;

    public void Report(RuntimePreparationProgress value)
    {
        if (value.Stage == current) return;
        current = value.Stage;
        Console.WriteLine($"QA_RUNTIME={current}");
    }
}
