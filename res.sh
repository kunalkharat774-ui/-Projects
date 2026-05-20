#!/bin/bash

# MSBTE Diploma Result Checker
# A fully functional Bash-based result lookup tool

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Clear screen
clear

# Function to display header
show_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${WHITE}          MAHARASHTRA STATE BOARD OF TECHNICAL         ${BLUE}║${NC}"
    echo -e "${BLUE}║${WHITE}               EDUCATION (MSBTE) - DIPLOMA             ${BLUE}║${NC}"
    echo -e "${BLUE}║${WHITE}                 RESULT CHECKING SYSTEM                 ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show menu
show_menu() {
    echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Select Exam Type:${NC}"
    echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}  1.${NC} Summer Exam Results"
    echo -e "${CYAN}  2.${NC} Winter Exam Results"
    echo -e "${CYAN}  3.${NC} Backlog / Re-Exam Results"
    echo -e "${CYAN}  4.${NC} Recent Results Summary"
    echo -e "${CYAN}  5.${NC} About MSBTE"
    echo -e "${CYAN}  6.${NC} Exit"
    echo ""
    echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to display recent results info
show_recent_results() {
    clear
    show_header
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━ RECENT RESULTS ━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${WHITE}  ✅ Winter 2024 Diploma Results:${NC} ${GREEN}DECLARED${NC}"
    echo -e "${WHITE}     📅 Declared on:${NC} February 2025"
    echo -e "${WHITE}     📍 Check at:${NC} msbte.ac.in / msbte.org.in"
    echo ""
    echo -e "${WHITE}  ✅ Summer 2024 Diploma Results:${NC} ${GREEN}DECLARED${NC}"
    echo -e "${WHITE}     📅 Declared on:${NC} July 2024"
    echo ""
    echo -e "${WHITE}  ✅ Winter 2023 Diploma Results:${NC} ${GREEN}DECLARED${NC}"
    echo -e "${WHITE}     📅 Declared on:${NC} February 2024"
    echo ""
    echo -e "${YELLOW}  ℹ️  Press ENTER to go back to main menu${NC}"
    read -r
}

# Function for actual result checking logic
check_result() {
    local exam_type=$1
    clear
    show_header

    echo -e "${GREEN}━━━━━━━━━━━━━━━ RESULT ENTRY FORM ━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Get enrollment number
    echo -e "${WHITE}  Enter Enrollment Number (e.g., 2301234567):${NC} "
    echo -n "  ➤ "
    read -r enrollment

    # Validate enrollment (basic check)
    if [[ -z "$enrollment" ]]; then
        echo -e "${RED}  ❌ Enrollment number cannot be empty!${NC}"
        echo ""
        echo -e "${YELLOW}  ℹ️  Press ENTER to try again${NC}"
        read -r
        return
    fi

    # Get mother's name
    echo -e "${WHITE}  Enter Mother's Name (as on records):${NC} "
    echo -n "  ➤ "
    read -r mother_name

    if [[ -z "$mother_name" ]]; then
        echo -e "${RED}  ❌ Mother's name cannot be empty!${NC}"
        echo ""
        echo -e "${YELLOW}  ℹ️  Press ENTER to try again${NC}"
        read -r
        return
    fi

    # Semester selection
    echo ""
    echo -e "${WHITE}  Select Semester:${NC}"
    echo -e "${CYAN}    1.${NC} 1st Semester"
    echo -e "${CYAN}    2.${NC} 2nd Semester"
    echo -e "${CYAN}    3.${NC} 3rd Semester"
    echo -e "${CYAN}    4.${NC} 4th Semester"
    echo -e "${CYAN}    5.${NC} 5th Semester"
    echo -e "${CYAN}    6.${NC} 6th Semester"
    echo -n "  ➤ "
    read -r sem_choice

    # Validate semester choice
    if [[ ! "$sem_choice" =~ ^[1-6]$ ]]; then
        echo -e "${RED}  ❌ Invalid semester choice!${NC}"
        echo ""
        echo -e "${YELLOW}  ℹ️  Press ENTER to try again${NC}"
        read -r
        return
    fi

    semesters=("1st" "2nd" "3rd" "4th" "5th" "6th")
    semester=${semesters[$((sem_choice - 1))]}

    # Simulate processing
    echo ""
    echo -e "${YELLOW}  ⏳ Fetching your result..."
    sleep 1

    # Show result (simulated - in real scenario this would hit MSBTE API)
    clear
    show_header

    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${WHITE}                      RESULT CARD                       ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${WHITE}  Enrollment No:${NC} ${CYAN}$enrollment${NC}"
    echo -e "${WHITE}  Student Name:${NC} ${CYAN}[REDACTED - Will be fetched from DB]${NC}"
    echo -e "${WHITE}  Mother's Name:${NC} ${CYAN}$mother_name${NC}"
    echo -e "${WHITE}  Exam Type:${NC} ${CYAN}$exam_type${NC}"
    echo -e "${WHITE}  Semester:${NC} ${CYAN}$semester Semester${NC}"
    echo ""
    echo -e "${YELLOW}────────────────────────────────────────────────────────${NC}"
    echo ""

    # Simulated subject marks
    subjects=("Applied Mathematics" "Applied Physics" "Applied Chemistry" "Communication Skills" "Engineering Drawing" "Computer Fundamentals")
    marks=()
    total=0
    max_marks=100

    for subject in "${subjects[@]}"; do
        mark=$((RANDOM % 31 + 70))  # Random marks between 70-100
        marks+=("$mark")
        total=$((total + mark))
    done

    percentage=$((total / 6))

    echo -e "${WHITE}  📚 Subject-wise Performance:${NC}"
    echo ""
    for i in "${!subjects[@]}"; do
        subject="${subjects[$i]}"
        mark="${marks[$i]}"

        if [[ $mark -ge 85 ]]; then
            grade="${GREEN}O (Outstanding)${NC}"
        elif [[ $mark -ge 75 ]]; then
            grade="${GREEN}A+ (Excellent)${NC}"
        elif [[ $mark -ge 65 ]]; then
            grade="${CYAN}A (Very Good)${NC}"
        elif [[ $mark -ge 55 ]]; then
            grade="${YELLOW}B+ (Good)${NC}"
        elif [[ $mark -ge 50 ]]; then
            grade="${YELLOW}B (Average)${NC}"
        else
            grade="${RED}C (Pass)${NC}"
        fi

        printf "  ${WHITE}%-30s${NC} : ${BOLD}%3d${NC}/$max_marks → $grade\n" "$subject" "$mark"
    done

    echo ""
    echo -e "${YELLOW}────────────────────────────────────────────────────────${NC}"
    echo ""

    # Result summary
    echo -e "${WHITE}  📊 Result Summary:${NC}"
    echo ""
    echo -e "     ${WHITE}Total Marks:${NC} ${BOLD}$total${NC} / $((6 * max_marks))"
    echo -e "     ${WHITE}Percentage:${NC} ${BOLD}$percentage%${NC}"

    if [[ $percentage -ge 75 ]]; then
        result_status="${GREEN}✅ PASSED WITH DISTINCTION${NC}"
        result_color="${GREEN}"
    elif [[ $percentage -ge 60 ]]; then
        result_status="${GREEN}✅ PASSED WITH FIRST CLASS${NC}"
        result_color="${GREEN}"
    elif [[ $percentage -ge 50 ]]; then
        result_status="${GREEN}✅ PASSED WITH SECOND CLASS${NC}"
        result_color="${GREEN}"
    elif [[ $percentage -ge 40 ]]; then
        result_status="${GREEN}✅ PASSED${NC}"
        result_color="${GREEN}"
    else
        result_status="${RED}❌ FAILED${NC}"
        result_color="${RED}"
    fi

    echo -e "     ${WHITE}Result:${NC} $result_status"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}  ℹ️  This is a simulated result for demonstration purposes.${NC}"
    echo -e "${YELLOW}     Real results require actual API integration with MSBTE.${NC}"
    echo ""
    echo -e "${WHITE}  Press ENTER to continue${NC}"
    read -r
}

# Function: About MSBTE
show_about() {
    clear
    show_header
    echo -e "${GREEN}━━━━━━━━━━━━━━━━ ABOUT MSBTE ━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${WHITE}  Maharashtra State Board of Technical Education${NC}"
    echo -e "${WHITE}  (MSBTE)${NC}"
    echo ""
    echo -e "${CYAN}  📍 Address:${NC}"
    echo -e "     4th Floor, Government Polytechnic Building,"
    echo -e "     49, Kherwadi, Bandra (East),"
    echo -e "     Mumbai - 400051, Maharashtra, India"
    echo ""
    echo -e "${CYAN}  🌐 Website:${NC} https://msbte.org.in"
    echo -e "${CYAN}  🌐 Result Portal:${NC} https://msbte.ac.in"
    echo ""
    echo -e "${CYAN}  📞 Contact:${NC}"
    echo -e "     Phone: 022-2647 1385 / 022-2647 1386"
    echo -e "     Email: info@msbte.org.in"
    echo ""
    echo -e "${CYAN}  ℹ️ About:${NC}"
    echo -e "     MSBTE conducts diploma examinations in"
    echo -e "     engineering, technology, and other fields"
    echo -e "     across Maharashtra state."
    echo ""
    echo -e "${YELLOW}  ℹ️  Press ENTER to go back${NC}"
    read -r
}

# ============== MAIN PROGRAM LOOP ==============

while true; do
    clear
    show_header
    show_menu

    echo -n -e "${GREEN}  Enter your choice [1-6]:${NC} "
    read -r choice

    case $choice in
        1)
            check_result "Summer Exam"
            ;;
        2)
            check_result "Winter Exam"
            ;;
        3)
            check_result "Backlog / Re-Exam"
            ;;
        4)
            show_recent_results
            ;;
        5)
            show_about
            ;;
        6)
            clear
            echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║${WHITE}          Thank you for using MSBTE Result Checker     ${GREEN}║${NC}"
            echo -e "${GREEN}║${WHITE}                 Good luck with your results!           ${GREEN}║${NC}"
            echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}  ❌ Invalid choice. Please enter 1-6.${NC}"
            sleep 1
            ;;
    esac
done
