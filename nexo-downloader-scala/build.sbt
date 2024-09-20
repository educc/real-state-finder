val scala3Version = "2.13.14"
val circeVersion = "0.14.1"
val sttpVersion = "3.9.8"

lazy val root = project
  .in(file("."))
  .settings(
    name := "nexo-downloader-scala",
    version := "0.1.0-SNAPSHOT",
    scalaVersion := scala3Version,
    // DEPS
    libraryDependencies ++= Seq(
      "com.softwaremill.sttp.client3" %% "core",
      "com.softwaremill.sttp.client3" %% "okhttp-backend"
    ).map(_ % sttpVersion),
    libraryDependencies ++= Seq(
      "com.typesafe.scala-logging" %% "scala-logging" % "3.9.5",
      "ch.qos.logback" % "logback-classic" % "1.5.8"
    ),
    libraryDependencies ++= Seq(
      "com.lihaoyi" %% "upickle" % "4.0.0"
    ),
    libraryDependencies ++= Seq(
      "dev.zio" %% "zio" % "2.1.9"
    ),
    // TESTS
    libraryDependencies += "org.scalameta" %% "munit" % "1.0.0" % Test
  )
