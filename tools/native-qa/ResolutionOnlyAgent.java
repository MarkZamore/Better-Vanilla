import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

/** QA only. Stop at Minecraft's main method, after Fabric resolves the mods. */
public final class ResolutionOnlyAgent {
    public static void premain(String arguments, Instrumentation instrumentation) {
        instrumentation.addTransformer(new ClassFileTransformer() {
            @Override
            public byte[] transform(ClassLoader loader, String name, Class<?> type,
                    ProtectionDomain domain, byte[] bytes) {
                if (!"net/minecraft/client/main/Main".equals(name)) return null;
                ClassReader reader = new ClassReader(bytes);
                ClassWriter writer = new ClassWriter(reader, 0);
                reader.accept(new ClassVisitor(Opcodes.ASM9, writer) {
                    @Override
                    public MethodVisitor visitMethod(int access, String method, String descriptor,
                            String signature, String[] exceptions) {
                        if (method.equals("main") && descriptor.equals("([Ljava/lang/String;)V")) return null;
                        return super.visitMethod(access, method, descriptor, signature, exceptions);
                    }

                    @Override
                    public void visitEnd() {
                        MethodVisitor method = super.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC,
                            "main", "([Ljava/lang/String;)V", null, null);
                        method.visitCode();
                        method.visitFieldInsn(Opcodes.GETSTATIC, "java/lang/System", "out", "Ljava/io/PrintStream;");
                        method.visitLdcInsn("FABRIC_RESOLUTION_ONLY_PASS");
                        method.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/io/PrintStream", "println",
                            "(Ljava/lang/String;)V", false);
                        method.visitInsn(Opcodes.RETURN);
                        method.visitMaxs(2, 1);
                        method.visitEnd();
                        super.visitEnd();
                    }
                }, 0);
                return writer.toByteArray();
            }
        });
    }
}
