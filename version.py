"""
Version configuration for Web Style Extractor
"""

__version__ = "1.2.0"
__release_status__ = "stable"  # options: alpha, beta, rc, stable
__build_date__ = "2025-09-03"

def get_version_string():
    """Get formatted version string"""
    return f"v{__version__}"

def get_full_version_info():
    """Get complete version information"""
    return {
        'version': __version__,
        'status': __release_status__,
        'build_date': __build_date__,
        'display_name': f"Web Style Extractor v{__version__}"
    }

def is_stable():
    """Check if this is a stable release"""
    return __release_status__ == "stable"

def get_display_name():
    """Get display name for the application"""
    if __release_status__ == "stable":
        return f"Web Style Extractor v{__version__}"
    else:
        return f"Web Style Extractor v{__version__}-{__release_status__}"