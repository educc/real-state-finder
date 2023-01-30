import io.circe.parser.parse
import io.circe.{Decoder, HCursor}
import scala.util.Try
import java.math.MathContext
import java.nio.file.{Files, Paths}

object NexoInmobiliariaFinder {

  val source = "./data/search_data.json"

  private implicit val decoder: Decoder[ApartmentItem] = new Decoder[ApartmentItem] {
    final def apply(c: HCursor): Decoder.Result[ApartmentItem] =
      for {
        district <- c.downField("distrito").as[String]
        address <- c.downField("direccion").as[String]
        phone1 <- c.downField("project_phone").as[String]
        phone2 <- c.downField("project_cell_phone").as[String]
        phone3 <- c.downField("project_whatsapp").as[String]
        currency <- c.downField("coin").as[String]
        minPrice <- c.downField("min_price").as[BigDecimal]
        minArea <- c.downField("area_min").as[BigDecimal]
        maxArea <- c.downField("area_max").as[BigDecimal]
        url <- c.downField("url").as[String]
      } yield {
        val contact = Seq(phone1, phone2, phone3)
          .map(_.trim)
          .map(_.replace(",","-"))
          .filter(_.length>0)
        val exchangeRate = if (currency == "S/.") 1 else 4
        val price = exchangeRate * minPrice
        val priceBy = Try {
          (price/minArea).setScale(0, BigDecimal.RoundingMode.UP)
        }.getOrElse(BigDecimal(0))
        
        val cleanAddress = address.replace(",", " ")
        ApartmentItem(district, cleanAddress, priceBy,minArea, maxArea, url, contact)
      }
  }


  def find : Seq[ApartmentItem] = {
    parse(readFile)
      .flatMap(_.as[Seq[ApartmentItem]])
      .getOrElse(Seq.empty)
  }

  private def readFile = Files.readString(Paths.get(source))

}
