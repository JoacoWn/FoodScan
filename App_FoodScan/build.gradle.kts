// build.gradle.kts (Archivo de nivel de PROYECTO)

// Este bloque define los plugins que están disponibles para los submódulos.
plugins {
    // Aquí se define la versión del Android Gradle Plugin (AGP).
    // Usaremos la versión 8.9.2 (la que te dio el error) para asegurar consistencia.
    id("com.android.application") version "8.9.2" apply false
    // Si usas Kotlin en tu proyecto, también es crucial declararlo aquí.
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false // Asegúrate de la versión de Kotlin adecuada
}

// Tarea para limpiar el directorio de compilación del proyecto.
tasks.register("clean", org.gradle.api.tasks.Delete::class) {
    delete(rootProject.buildDir)
}