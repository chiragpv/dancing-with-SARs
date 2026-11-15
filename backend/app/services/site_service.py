from app.models.site import Site, SiteKey

SITES: tuple[Site, ...] = (
    Site(
        key=SiteKey.BRAHMAPUTRA,
        name="Brahmaputra",
        latitude=26.2,
        longitude=91.7,
        description=(
            "Project-configured illustrative observation point. Coordinates do not "
            "define a satellite acquisition footprint."
        ),
    ),
    Site(
        key=SiteKey.WAYANAD,
        name="Wayanad",
        latitude=11.6,
        longitude=76.1,
        description=(
            "Project-configured illustrative observation point. Coordinates do not "
            "define a satellite acquisition footprint."
        ),
    ),
    Site(
        key=SiteKey.AMAZON,
        name="Amazon",
        latitude=-9.0,
        longitude=-63.0,
        description=(
            "Project-configured illustrative observation point. Coordinates do not "
            "define a satellite acquisition footprint."
        ),
    ),
    Site(
        key=SiteKey.LADAKH,
        name="Ladakh",
        latitude=34.2,
        longitude=77.6,
        description=(
            "Project-configured illustrative observation point. Coordinates do not "
            "define a satellite acquisition footprint."
        ),
    ),
)


def list_sites() -> tuple[Site, ...]:
    return SITES
