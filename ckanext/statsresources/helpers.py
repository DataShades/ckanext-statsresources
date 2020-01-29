def get_org_title(pkg):
    """Return title of pkg's organization."""
    orgs = pkg.get_groups("organization")
    return orgs.pop().title if orgs else ""
