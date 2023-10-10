import io.circe.parser.parse
import io.circe.{Decoder, HCursor}
import scala.util.Try
import java.math.MathContext

object ApartmentItem {

  implicit val apartmentItemDecoder: Decoder[ApartmentItem] =
    new Decoder[ApartmentItem] {
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
          slug <- c.downField("slug").as[String]
          projectPhase <- c.downField("project_phase").as[String]
        } yield {
          val contact = Seq(phone1, phone2, phone3)
            .map(_.trim)
            .map(_.replace(",", "-"))
            .filter(_.length > 0)
          val exchangeRate = if (currency == "S/.") 1 else 4
          val price = exchangeRate * minPrice
          val priceBy = Try {
            (price / minArea).setScale(0, BigDecimal.RoundingMode.UP)
          }.getOrElse(BigDecimal(0))

          val cleanAddress = address.replace(",", " ")
          val url = s"https://google.com/search?q=$slug"
          val phase = projectPhase match {
            case "1"       => "En planos"
            case "2"       => "Construcción"
            case "3"       => "Entrega inmediata"
            case _: String => projectPhase
          }
          val roomMin = 0
          val roomMax = 0

          ApartmentItem(
            district,
            cleanAddress,
            priceBy,
            minArea,
            maxArea,
            roomMin,
            roomMax,
            url,
            phase,
            contact
          )
        }
    }
}

case class ApartmentItem(
    district: String,
    address: String,
    priceByM2: BigDecimal,
    areaMin: BigDecimal,
    areaMax: BigDecimal,
    roomMin: Int,
    roomMax: Int,
    url: String,
    phase: String,
    contact: Seq[String] = Seq.empty
) {
  def toCsv: String = {
    Seq(
      district,
      address,
      priceByM2,
      areaMin,
      areaMax,
      roomMin,
      roomMax,
      phase,
      contact,
      url
    )
      .map {
        case a: Seq[_] => a.mkString("-")
        case b         => b.toString
      }
      .mkString(",")

  }
}
