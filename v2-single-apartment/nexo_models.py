from dataclasses import dataclass, field


@dataclass
class ProjectInfo:
    area_max: str | None = None
    area_min: str | None = None
    bathroom_max: str | None = None
    bathroom_min: str | None = None
    builder_name: str | None = None
    builder_slug: str | None = None
    cantidad: str | None = None
    cintillo_principal: str | None = None
    coin: str | None = None
    coord_lat: str | None = None
    direccion: str | None = None
    distrito: str | None = None
    dpto_project: str | None = None
    finance_bank: str | None = None
    gallery: list[str] = field(default_factory=list)
    gallery_big: list[str] = field(default_factory=list)
    gallery_xm: list[str] = field(default_factory=list)
    image: str | None = None
    important_level: str | None = None
    is_featured: str | None = None
    keyword: str | None = None
    logo_empresa: str | None = None
    long: str | None = None
    min_price: str | None = None
    name: str | None = None
    parking_max: str | None = None
    parking_min: str | None = None
    project_cell_phone: str | None = None
    project_contact: str | None = None
    project_email: str | None = None
    project_id: str | None = None
    project_phase: str | None = None
    project_phone: str | None = None
    project_whatsapp: str | None = None
    provincia_project: str | None = None
    room_max: str | None = None
    room_min: str | None = None
    services: str | None = None
    slug: str | None = None
    socio_asei: str | None = None
    tiene_promo_fn: str | None = None
    tour_virtual: str | None = None
    type_project: str | None = None
    url: str | None = None
    url_video: str | None = None
    val_price1: str | None = None
    val_price2: str | None = None
    visibility_ferianexo: str | None = None
    visibility_in_feria_nexo: str | None = None
    visibility_semananexo: str | None = None

    def __post_init__(self):
        # Convert comma-separated strings to lists
        self.gallery = self.gallery.split(',') if self.gallery else []
        self.gallery_xm = self.gallery_xm.split(',') if self.gallery_xm else []
        self.gallery_big = self.gallery_big.split(
            ',') if self.gallery_big else []

    @staticmethod
    def from_dict(data: dict) -> 'ProjectInfo':
        return ProjectInfo(
            area_max=data.get("area_max"),
            area_min=data.get("area_min"),
            bathroom_max=data.get("bathroom_max"),
            bathroom_min=data.get("bathroom_min"),
            builder_name=data.get("builder_name"),
            builder_slug=data.get("builder_slug"),
            cantidad=data.get("cantidad"),
            cintillo_principal=data.get("cintillo_principal"),
            coin=data.get("coin"),
            coord_lat=data.get("coord_lat"),
            direccion=data.get("direccion"),
            distrito=data.get("distrito"),
            dpto_project=data.get("dpto_project"),
            finance_bank=data.get("finance_bank"),
            gallery=data.get("gallery"),
            gallery_big=data.get("gallery_big"),
            gallery_xm=data.get("gallery_xm"),
            image=data.get("image"),
            important_level=data.get("important_level"),
            is_featured=data.get("is_featured"),
            keyword=data.get("keyword"),
            logo_empresa=data.get("logo_empresa"),
            long=data.get("long"),
            min_price=data.get("min_price"),
            name=data.get("name"),
            parking_max=data.get("parking_max"),
            parking_min=data.get("parking_min"),
            project_cell_phone=data.get("project_cell_phone"),
            project_contact=data.get("project_contact"),
            project_email=data.get("project_email"),
            project_id=data.get("project_id"),
            project_phase=data.get("project_phase"),
            project_phone=data.get("project_phone"),
            project_whatsapp=data.get("project_whatsapp"),
            provincia_project=data.get("provincia_project"),
            room_max=data.get("room_max"),
            room_min=data.get("room_min"),
            services=data.get("services"),
            slug=data.get("slug"),
            socio_asei=data.get("socio_asei"),
            tiene_promo_fn=data.get("tiene_promo_fn"),
            tour_virtual=data.get("tour_virtual"),
            type_project=data.get("type_project"),
            url=data.get("url"),
            url_video=data.get("url_video"),
            val_price1=data.get("val_price1"),
            val_price2=data.get("val_price2"),
            visibility_ferianexo=data.get("visibility_ferianexo"),
            visibility_in_feria_nexo=data.get("visibility_in_feria_nexo"),
            visibility_semananexo=data.get("visibility_semananexo"),
        )