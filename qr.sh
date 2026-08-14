#!/usr/bin/env bash
#===============================================================================
#  URL QR Code Generator
#  High-quality QR code generator for URLs with rich customization options
#  GitHub: https://github.com/yourusername/url-qr-generator
#  License: MIT
#===============================================================================

set -euo pipefail
IFS=$'\n\t'

#-------------------------------------------------------------------------------
#  CONFIGURATION
#-------------------------------------------------------------------------------
VERSION="2.1.0"
SCRIPT_NAME=$(basename "$0")

# Default values
DEFAULT_SCALE=20
DEFAULT_ECL="H"            # L(7%), M(15%), Q(25%), H(30%)
DEFAULT_FG="111111"        # Dark foreground (hex without #)
DEFAULT_BG="FFFFFF"        # White background
DEFAULT_OUTPUT="qr_code.png"
DEFAULT_FORMAT="png"

# ASCII art banner
readonly BANNER='''\033[1;36m
   ____  _   _    _   ___   ____   ___   ____ ___    _    ____  
  / __ \| \ | |  / \ |_ _| |  _ \ / _ \ / ___|_ _|  / \  |  _ \ 
 | |  | |  \| | / _ \ | |  | |_) | | | | |    | |  / _ \ | |_) |
 | |  | | |\  |/ ___ \| |  |  _ <| |_| | |___ | | / ___ \|  _ < 
 | |__| |_| \_/_/   \_\_|  |_| \_\\___/ \____|___/_/   \_\_| \_\
  \___\_\   \_\_/ \_/ \_/  |_| \_\\___/ \____|___/_/   \_\_| \_\
\033[0m'''

#-------------------------------------------------------------------------------
#  HELPER FUNCTIONS
#-------------------------------------------------------------------------------

print_banner() {
    echo -e "$BANNER"
    echo -e "\033[1;33m  URL QR Code Generator v$VERSION\033[0m"
    echo -e "\033[1;30m  ─────────────────────────────────────────────\033[0m"
    echo ""
}

usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] <URL>

Generate high-resolution QR codes from URLs with full customization.

REQUIRED:
  <URL>              The URL or text to encode into the QR code

OPTIONS:
  -o, --output FILE  Output filename (default: $DEFAULT_OUTPUT)
  -f, --format FMT   Output format: png, svg, eps (default: $DEFAULT_FORMAT)
  -s, --scale N      Module pixel size (default: $DEFAULT_SCALE, max: 100)
  -l, --level LVL    Error correction: L, M, Q, H (default: $DEFAULT_ECL)
                      L=7%, M=15%, Q=25%, H=30% recovery
  -c, --color HEX    Foreground color in hex (default: $DEFAULT_FG)
                      Example: ff0000 for red, 0000ff for blue
  -b, --bg HEX       Background color in hex (default: $DEFAULT_BG)
  -m, --margin N     Quiet zone margin in modules (default: 4)
  -v, --version      Display version and exit
  -h, --help         Display this help and exit

EXAMPLES:
  # Basic URL QR code
  $SCRIPT_NAME "https://github.com"

  # High-res with custom colors
  $SCRIPT_NAME -s 40 -c ff4444 -b ffffff -o my_qr.png "https://example.com"

  # SVG output for vectors
  $SCRIPT_NAME -f svg -s 10 -o logo.svg "https://mysite.com"

  # Maximum error correction for logo overlay
  $SCRIPT_NAME -l H -s 30 -o robust.png "https://myurl.com"

DEPENDENCIES:
  qrencode   - Core QR generation engine
  (Optional) imagemagick - For advanced post-processing

Install: bash <(curl -s https://raw.githubusercontent.com/yourusername/url-qr-generator/main/install.sh)
EOF
    exit 0
}

version() {
    echo "URL QR Code Generator v$VERSION"
    echo "Copyright (c) 2024-2026"
    echo "License: MIT"
    exit 0
}

error_exit() {
    echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
    exit 1
}

info() {
    echo -e "\033[1;34m[*]\033[0m $1"
}

success() {
    echo -e "\033[1;32m[+]\033[0m $1"
}

warn() {
    echo -e "\033[1;33m[!]\033[0m $1"
}

#-------------------------------------------------------------------------------
#  DEPENDENCY CHECK
#-------------------------------------------------------------------------------

check_dependencies() {
    local missing=()
    
    if ! command -v qrencode &>/dev/null; then
        missing+=("qrencode")
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "\033[1;31m[ERROR] Missing dependencies: ${missing[*]}\033[0m"
        echo ""
        echo "Install them using your package manager:"
        echo "  Ubuntu/Debian:  sudo apt-get install ${missing[*]}"
        echo "  Fedora/RHEL:    sudo dnf install ${missing[*]}"
        echo "  Arch Linux:     sudo pacman -S ${missing[*]}"
        echo "  macOS:          brew install ${missing[*]}"
        echo ""
        echo "Or run the automated installer:"
        echo "  bash <(curl -s https://raw.githubusercontent.com/yourusername/url-qr-generator/main/install.sh)"
        exit 1
    fi
    
    # Check qrencode version (need >= 4.0.0 for color support)
    local qr_version
    qr_version=$(qrencode --version 2>&1 | head -1 | grep -oP '[\d]+\.[\d]+' || echo "0")
    if [[ $(echo "$qr_version < 4.0" | bc -l 2>/dev/null) == "1" || "$qr_version" == "0" ]]; then
        warn "qrencode version $qr_version detected. Version 4.0+ recommended for color support."
    fi
}

#-------------------------------------------------------------------------------
#  OUTPUT SIZE CALCULATION
#-------------------------------------------------------------------------------

calculate_dimensions() {
    local scale=$1
    local margin=$2
    local version=${3:-0}
    
    # QR code has 21 + (version-1)*4 modules per side
    # If version is auto-detected (0), assume max reasonable size
    local modules
    if [[ $version -gt 0 ]]; then
        modules=$((21 + (version - 1) * 4))
    else
        modules=33  # Rough average for URLs
    fi
    
    local total_modules=$((modules + margin * 2))
    local total_pixels=$((total_modules * scale))
    
    echo "$total_pixels"
}

#-------------------------------------------------------------------------------
#  MAIN QR GENERATION
#-------------------------------------------------------------------------------

generate_qr() {
    local url="$1"
    local output="$2"
    local format="$3"
    local scale="$4"
    local ecl="$5"
    local fg_color="$6"
    local bg_color="$7"
    local margin="$8"
    
    info "Encoding:  $url"
    info "Output:    $output"
    info "Format:    $format"
    info "Scale:     $scale px/module"
    info "EC Level:  $ecl"
    info "Foreground: #$fg_color"
    info "Background: #$bg_color"
    info "Margin:    $margin modules"
    
    # Build qrencode command
    local cmd=("qrencode")
    
    # Set output format
    if [[ "$format" == "png" ]]; then
        cmd+=(-t PNG)
    elif [[ "$format" == "svg" ]]; then
        cmd+=(-t SVG)
    elif [[ "$format" == "eps" ]]; then
        cmd+=(-t EPS)
    else
        error_exit "Unsupported format: $format (use png, svg, or eps)"
    fi
    
    # Set error correction level
    cmd+=(-l "$ecl")
    
    # Set module size (scale)
    cmd+=(-s "$scale")
    
    # Set margin (quiet zone)
    cmd+=(-m "$margin")
    
    # Set colors (qrencode 4.0+)
    cmd+=(--foreground="$fg_color" --background="$bg_color")
    
    # Set output file
    cmd+=(-o "$output")
    
    # Set the data (URL)
    cmd+=("$url")
    
    info "Running: ${cmd[*]}"
    echo ""
    
    # Execute
    if "${cmd[@]}"; then
        local file_size
        file_size=$(du -h "$output" 2>/dev/null | cut -f1 || echo "unknown")
        
        success "QR code generated successfully!"
        echo ""
        echo "  File:      $output"
        echo "  Size:      $file_size"
        
        # If ImageMagick is available, show image dimensions
        if command -v identify &>/dev/null; then
            local dims
            dims=$(identify -format "%wx%d" "$output" 2>/dev/null || true)
            if [[ -n "$dims" ]]; then
                echo "  Dimensions: $dims pixels"
            fi
        fi
        
        echo ""
        echo "  Scan the QR code to visit: $url"
        return 0
    else
        error_exit "QR code generation failed!"
    fi
}

#-------------------------------------------------------------------------------
#  POST-PROCESSING (Optional enhancements with ImageMagick)
#-------------------------------------------------------------------------------

post_process() {
    local output="$1"
    local format="$2"
    
    if ! command -v convert &>/dev/null; then
        return 0  # ImageMagick not available, skip
    fi
    
    if [[ "$format" != "png" ]]; then
        return 0  # Only post-process PNG
    fi
    
    # Add subtle rounded corners for aesthetics (optional)
    # convert "$output" -alpha set -background none \
    #     \( +clone -alpha extract -draw "roundrectangle 0,0,%[w],%[h],15,15" \) \
    #     -alpha off -compose copy_opacity -composite "$output" 2>/dev/null || true
}

#-------------------------------------------------------------------------------
#  PARSE ARGUMENTS
#-------------------------------------------------------------------------------

parse_args() {
    local args=("$@")
    local i=0
    
    URL=""
    OUTPUT="$DEFAULT_OUTPUT"
    FORMAT="$DEFAULT_FORMAT"
    SCALE=$DEFAULT_SCALE
    ECL="$DEFAULT_ECL"
    FG="$DEFAULT_FG"
    BG="$DEFAULT_BG"
    MARGIN=4
    
    while [[ $i -lt ${#args[@]} ]]; do
        case "${args[$i]}" in
            -o|--output)
                i=$((i+1))
                if [[ $i -ge ${#args[@]} ]]; then
                    error_exit "--output requires a filename argument"
                fi
                OUTPUT="${args[$i]}"
                ;;
            -f|--format)
                i=$((i+1))
                if [[ $i -ge ${#args[@]} ]]; then
                    error_exit "--format requires an argument (png|svg|eps)"
                fi
                FORMAT="${args[$i]}"
                ;;
            -s|--scale)
                i=$((i+1))
                if [[ $i -ge ${#args[@]} ]]; then
                    error_exit "--scale requires a number argument"
                fi
                SCALE="${args[$i]}"
                if [[ $SCALE -lt 1 || $SCALE -gt 100 ]]; then
                    error_exit "Scale must be between 1 and 100"
                fi
                ;;
            -l|--level)
                i=$((i+1))
                if [[ $i -ge ${#args[@]} ]]; then
                    error_exit "--level requires L, M, Q, or H"
                fi
                ECL="${args[$i]^^}"
                if [[ ! "$ECL" =~ ^[LMQH]$ ]]; then
                    error_exit "Error correction level must be L, M, Q, or H"
                fi
                ;;
            -c|--color)
                i=$((i+1))
                if [[ $i -ge ${#args[@]} ]]; then
                    error_exit "--color requires a hex color argument"
                fi
                FG="${args[$i]#\#}"
                if [[ ! "$FG" =~ ^[0-9a-fA-F]{6}$ ]]; then
                    error_exit "Foreground color must be a 6-digit hex value (e.g., ff0000)"
                fi
                ;;
            -b|--bg)
                i=$((i+1))
                if [[ $i -ge ${#args[@]} ]]; then
                    error_exit "--bg requires a hex color argument"
                fi
                BG="${args[$i]#\#}"
                if [[ ! "$BG" =~ ^[0-9a-fA-F]{6}$ ]]; then
                    error_exit "Background color must be a 6-digit hex value (e.g., ffffff)"
                fi
                ;;
            -m|--margin)
                i=$((i+1))
                if [[ $i -ge ${#args[@]} ]]; then
                    error_exit "--margin requires a number argument"
                fi
                MARGIN="${args[$i]}"
                if [[ $MARGIN -lt 0 || $MARGIN -gt 20 ]]; then
                    error_exit "Margin must be between 0 and 20"
                fi
                ;;
            -v|--version)
                version
                ;;
            -h|--help)
                usage
                ;;
            -*)
                error_exit "Unknown option: ${args[$i]} (use --help for usage)"
                ;;
            *)
                if [[ -z "$URL" ]]; then
                    URL="${args[$i]}"
                else
                    error_exit "Unexpected argument: ${args[$i]}"
                fi
                ;;
        esac
        i=$((i+1))
    done
    
    # Validate URL argument
    if [[ -z "$URL" ]]; then
        # Check if data is being piped
        if [[ ! -t 0 ]]; then
            read -r URL
        fi
    fi
    
    if [[ -z "$URL" ]]; then
        error_exit "No URL provided. Usage: $SCRIPT_NAME <URL>"
    fi
    
    # Auto-detect format from output filename if not explicitly set
    if [[ "$OUTPUT" == "$DEFAULT_OUTPUT" && "$FORMAT" == "png" ]]; then
        # Keep defaults
        :
    fi
    
    # Add extension if missing
    case "$FORMAT" in
        png) [[ "$OUTPUT" != *.png ]] && OUTPUT="${OUTPUT}.png" ;;
        svg) [[ "$OUTPUT" != *.svg ]] && OUTPUT="${OUTPUT}.svg" ;;
        eps) [[ "$OUTPUT" != *.eps ]] && OUTPUT="${OUTPUT}.eps" ;;
    esac
}

#-------------------------------------------------------------------------------
#  ENTRY POINT
#-------------------------------------------------------------------------------

main() {
    print_banner
    
    check_dependencies
    parse_args "$@"
    
    echo -e "\033[1;30m  ─────────────────────────────────────────────\033[0m"
    echo ""
    
    generate_qr "$URL" "$OUTPUT" "$FORMAT" "$SCALE" "$ECL" "$FG" "$BG" "$MARGIN"
    
    # Optional post-processing
    post_process "$OUTPUT" "$FORMAT"
    
    echo ""
    echo -e "\033[1;30m  ─────────────────────────────────────────────\033[0m"
    echo -e "\033[1;32m  ✓ Done — scan away!\033[0m"
}

# Run
main "$@"
