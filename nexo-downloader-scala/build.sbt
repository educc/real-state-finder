val scala3Version = "3.5.0"
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
      "io.circe" %% "circe-core",
      "io.circe" %% "circe-generic",
      "io.circe" %% "circe-parser"
    ).map(_ % circeVersion),
    libraryDependencies ++= Seq(
      "com.typesafe.scala-logging" %% "scala-logging" % "3.9.5",
      "ch.qos.logback" % "logback-classic" % "1.5.8"
    ),
    // TESTS
    libraryDependencies += "org.scalameta" %% "munit" % "1.0.0" % Test
  )
