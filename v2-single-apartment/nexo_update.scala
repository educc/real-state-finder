//> using scala 3
//> using toolkit 0.4.0
//> using dep dev.zio::zio:2.1.9
//> using dep dev.zio::zio-http:3.0.0-RC9
//> using dep io.circe::circe-core:0.14.1
//> using dep io.circe::circe-generic:0.14.1
//> using dep io.circe::circe-parser:0.14.1

import zio._
import zio.http._
import zio.Console._
import io.circe._, io.circe.parser._

object MainApp extends ZIOAppDefault {

  private val okHttpClient: OkHttpClient = OkHttpClient
  private val backend = OkHttpFutureBackend.usingClient(okHttpClient)
  private val NEXO_URL: String =
    "https://nexoinmobiliario.pe/departamentos/departamentos-lima"

  // Function to fetch and parse JSON data
  def fetchJsonData(url: String): ZIO[Client, Throwable, Json] = {
    for {
      client <- ZIO.service[Client]
      request = Request.get(url)
      response <- client.request(request)
      responseAsText <- response.body.asString
      jsonString = responseAsText
        .lines()
        .map(_.trim)
        .filter(_.contains("search_data"))
        .map(it => {
          val start = it.indexOf("[")
          val end = it.lastIndexOf("]")
          it.substring(start, end + 1)
        })
        .findFirst()
        .orElse("[]")
      json <- ZIO.fromEither(parse(jsonString))
    } yield json
  }

  val app =
    for {
      json <- fetchJsonData(NEXO_URL)
      _ <- printLine(s"Response: ${json}")
    } yield ()

  def run = app.provide(Client.default)
}

trait SimpleClient:
  def get(url: String): Task[String]

object Slug:
  def apply(input: String) = slugify(input)

  def slugify(input: String): String = {
    import java.text.Normalizer
    Normalizer
      .normalize(input, Normalizer.Form.NFD)
      .replaceAll(
        "[^\\w\\s-]",
        ""
      ) // Remove all non-word, non-space or non-dash characters
      .replace('-', ' ') // Replace dashes with spaces
      .trim // Trim leading/trailing whitespace (including what used to be leading/trailing dashes)
      .replaceAll(
        "\\s+",
        "-"
      ) // Replace whitespace (including newlines and repetitions) with single dashes
      .toLowerCase // Lowercase the final results
  }
