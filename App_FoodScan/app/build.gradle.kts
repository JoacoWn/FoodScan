// build.gradle.kts (Archivo del módulo 'app')

plugins {
    // Aplica el plugin de la aplicación Android.
    alias(libs.plugins.android.application)
    // Si estás usando Kotlin en este módulo, y has definido el alias:
    // alias(libs.plugins.kotlin.android)
    // NOTA: Si estás usando Kotlin en tus archivos .kt, necesitarás el plugin de Kotlin.
    // Si tu proyecto fue creado con plantilla de Kotlin, es probable que ya esté en el settings.gradle.kts y aquí también.
}

android {
    namespace = "com.example.app_foodscan"
    compileSdk = 35 // Mantener esta versión
    defaultConfig {
        applicationId = "com.example.app_foodscan"
        minSdk = 24
        targetSdk = 35 // Mantener esta versión
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    buildFeatures {
        viewBinding = true // Habilita View Binding
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11 // Java 11
        targetCompatibility = JavaVersion.VERSION_11 // Java 11
    }
    // Si usas Kotlin en tus archivos de código, puedes necesitar esto para el compilador de Kotlin
    // kotlinOptions {
    //     jvmTarget = "11"
    // }
}

dependencies {
    // Dependencias básicas de AndroidX (ya las tenías con libs).
    implementation(libs.appcompat)
    implementation(libs.material)

    // DEPENDENCIA CORREGIDA DE CARDVIEW: Ahora entre comillas dobles.
    implementation("androidx.cardview:cardview:1.0.0") // O puedes usar una versión más reciente si lo prefieres, por ejemplo, "1.0.0" es la más común

    // Dependencias para Retrofit, Gson y Glide.
    // Estas son las que causaban "Cannot resolve symbol" en tus archivos Java.
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")

    // Dependencia del Interceptor de Logging de OkHttp para ver logs de red
    implementation("com.squareup.okhttp3:logging-interceptor:4.9.0") // <--- ¡DEPENDENCIA AÑADIDA AQUÍ!

    implementation("com.github.bumptech.glide:glide:4.16.0")
    // Ojo: Si estás usando Kotlin, a veces el "annotationProcessor" se reemplaza por "kapt"
    // Pero si tu proyecto es Java puro, "annotationProcessor" es correcto.
    annotationProcessor("com.github.bumptech.glide:compiler:4.16.0")

    // Dependencias para pruebas (ya las tenías con libs).
    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
}