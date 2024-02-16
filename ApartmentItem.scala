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
          minPrice <- c.downField("val_price1").as[BigDecimal]
          maxPrice <- c.downField("val_price2").as[BigDecimal]
          minArea <- c.downField("area_min").as[BigDecimal]
          maxArea <- c.downField("area_max").as[BigDecimal]
          slug <- c.downField("slug").as[String]
          projectPhase <- c.downField("project_phase").as[String]
        } yield {
          ApartmentItemAdapter(
            district = district,
            address = address,
            phone1 = phone1,
            phone2 = phone2,
            phone3 = phone3,
            currency = currency,
            minPrice = minPrice,
            maxPrice = maxPrice,
            minArea = minArea,
            maxArea = maxArea,
            slug = slug,
            projectPhase = projectPhase
          ).convert()
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

private case class ApartmentItemAdapter(
    district: String,
    address: String,
    phone1: String,
    phone2: String,
    phone3: String,
    currency: String,
    minPrice: BigDecimal,
    maxPrice: BigDecimal,
    minArea: BigDecimal,
    maxArea: BigDecimal,
    slug: String,
    projectPhase: String
) {

  private val exchangeRate = if (currency == "S/.") 1 else 4
  private val minPriceSoles = exchangeRate * minPrice
  private val maxPriceSoles = exchangeRate * maxPrice

  private def mkDistrict: String = district

  private def mkAddress: String = address.replace(",", " ")

  private def mkPriceBySquare: BigDecimal = {
    Try {
      val squarePriceForMinArea = minPriceSoles / minArea
      val squarePriceForMaxArea = maxPriceSoles / maxArea
      val minSquarePrice =
        if (squarePriceForMaxArea > squarePriceForMinArea) squarePriceForMinArea
        else squarePriceForMaxArea

      minSquarePrice.setScale(0, BigDecimal.RoundingMode.UP)
    }.getOrElse(BigDecimal(0))
  }

  private def mkUrl: String = s"https://google.com/search?q=$slug"

  private def mkPhase: String = projectPhase match {
    case "1"       => "En planos"
    case "2"       => "Construcción"
    case "3"       => "Entrega inmediata"
    case _: String => projectPhase
  }

  private def mkContact: Seq[String] = {
    Seq(phone1, phone2, phone3)
      .map(_.trim)
      .map(_.replace(",", "-"))
      .filter(_.length > 0)
  }

  def convert(): ApartmentItem = {
    ApartmentItem(
      mkDistrict,
      mkAddress,
      mkPriceBySquare,
      minArea,
      maxArea,
      0,
      0,
      mkUrl,
      mkPhase,
      mkContact
    )
  }
}
