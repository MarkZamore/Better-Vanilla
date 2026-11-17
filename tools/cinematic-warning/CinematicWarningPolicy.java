package bettervanilla;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

/** Apply Cinematic's native acknowledgement before its client settings load. */
public final class CinematicWarningPolicy {
    private static final String KEY = "multiplayer.serverHintSeen";

    public static void premain(String arguments) {
        Path config = Path.of("config", "cinematic-client.json");
        Path pending = null;
        try {
            JsonObject settings = Files.exists(config)
                ? JsonParser.parseString(Files.readString(config, StandardCharsets.UTF_8)).getAsJsonObject()
                : new JsonObject();
            if (settings.has(KEY) && settings.get(KEY).isJsonPrimitive()
                    && settings.get(KEY).getAsJsonPrimitive().isBoolean()
                    && settings.get(KEY).getAsBoolean()) {
                return;
            }
            settings.addProperty(KEY, true);
            Files.createDirectories(config.getParent());
            pending = Files.createTempFile(config.getParent(), "cinematic-warning-", ".tmp");
            Files.writeString(pending, new GsonBuilder().setPrettyPrinting().create().toJson(settings) + "\n",
                StandardCharsets.UTF_8);
            try {
                Files.move(pending, config, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException unsupported) {
                Files.move(pending, config, StandardCopyOption.REPLACE_EXISTING);
            }
            System.out.println("[Better Vanilla] Cinematic server hint acknowledged.");
        } catch (Exception failure) {
            System.err.println("[Better Vanilla] Could not acknowledge Cinematic server hint: " + failure);
        } finally {
            if (pending != null) {
                try {
                    Files.deleteIfExists(pending);
                } catch (Exception failure) {
                    System.err.println("[Better Vanilla] Could not remove pending settings file: " + failure);
                }
            }
        }
    }
}
