
case class  ApartmentItem(
                         district: String,
                         address: String,
                         priceByM2: BigDecimal,
                         areaMin: BigDecimal,
                         areaMax: BigDecimal,
                         url: String,
                         contact: Seq[String] = Seq.empty
                         )
