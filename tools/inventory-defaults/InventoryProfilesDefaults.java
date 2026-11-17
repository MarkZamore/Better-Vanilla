package bettervanilla;

import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

/** Initialize IPN arrow visibility once, preserving later player choices. */
public final class InventoryProfilesDefaults {
    public static void premain(String arguments) {
        Path config = Path.of("config", "inventoryprofilesnext", "inventoryprofiles.json");
        Path marker = Path.of("config", "better-vanilla", "ipn-arrow-defaults-v1.applied");
        Path pending = null;
        try {
            if (Files.exists(marker) && Files.exists(config)) return;
            JsonObject settings = Files.exists(config)
                ? JsonParser.parseString(Files.readString(config, StandardCharsets.UTF_8)).getAsJsonObject()
                : new JsonObject();
            JsonObject refill = settings.has("AutoRefillSettings")
                ? settings.getAsJsonObject("AutoRefillSettings") : new JsonObject();
            disableToggle(refill, "auto_refill_enable_indicator_icons");
            disableToggle(refill, "auto_refill_enable_horbar_indicator_icons");
            settings.add("AutoRefillSettings", refill);
            Files.createDirectories(config.getParent());
            pending = Files.createTempFile(config.getParent(), "ipn-arrow-defaults-", ".tmp");
            Files.writeString(pending, new GsonBuilder().setPrettyPrinting().create().toJson(settings) + "\n",
                StandardCharsets.UTF_8);
            try {
                Files.move(pending, config, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException unsupported) {
                Files.move(pending, config, StandardCopyOption.REPLACE_EXISTING);
            }
            Files.createDirectories(marker.getParent());
            Files.writeString(marker, "IPN arrow defaults applied.\n", StandardCharsets.UTF_8);
        } catch (Exception failure) {
            System.err.println("[Better Vanilla] Could not apply IPN arrow defaults: " + failure);
        } finally {
            if (pending != null) {
                try {
                    Files.deleteIfExists(pending);
                } catch (Exception failure) {
                    System.err.println("[Better Vanilla] Could not remove pending IPN settings: " + failure);
                }
            }
        }
    }

    private static void disableToggle(JsonObject settings, String key) {
        if (settings.has(key) && settings.get(key).isJsonObject()) {
            settings.getAsJsonObject(key).addProperty("value", false);
        } else {
            settings.addProperty(key, false);
        }
    }
}
