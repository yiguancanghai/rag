#!/bin/bash

# IntelliDocs Pro Docker Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check environment file
check_env_file() {
    ENV_FILE="../config/.env"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file not found at $ENV_FILE"
        print_status "Creating environment file from template..."
        
        if [ -f "../config/.env.example" ]; then
            cp "../config/.env.example" "$ENV_FILE"
            print_warning "Please edit $ENV_FILE and add your OpenAI API key"
            print_status "Required: OPENAI_API_KEY=your_api_key_here"
            return 1
        else
            print_error "Environment template not found. Please create $ENV_FILE manually."
            return 1
        fi
    fi
    
    # Check if API key is set
    if ! grep -q "OPENAI_API_KEY=sk-" "$ENV_FILE" 2>/dev/null; then
        print_warning "OpenAI API key not found or not properly set in $ENV_FILE"
        print_status "Please add: OPENAI_API_KEY=your_api_key_here"
        return 1
    fi
    
    print_success "Environment file is configured"
    return 0
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/documents
    mkdir -p data/vector_db
    mkdir -p logs
    
    print_success "Directories created"
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    
    cd "$(dirname "$0")"
    
    docker build -t intellidocs-pro:latest -f Dockerfile ..
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run with docker-compose
run_compose() {
    print_status "Starting IntelliDocs Pro with docker-compose..."
    
    cd "$(dirname "$0")"
    
    # Load environment variables
    export $(grep -v '^#' ../config/.env | xargs)
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "IntelliDocs Pro is running!"
        print_status "Access the application at: http://localhost:8501"
        print_status "Use 'docker-compose down' to stop the application"
    else
        print_error "Failed to start the application"
        exit 1
    fi
}

# Function to run standalone container
run_standalone() {
    print_status "Starting IntelliDocs Pro as standalone container..."
    
    cd "$(dirname "$0")"
    
    # Load environment variables
    ENV_VARS=""
    if [ -f "../config/.env" ]; then
        while IFS= read -r line; do
            if [[ ! "$line" =~ ^# ]] && [[ "$line" =~ ^[A-Z] ]]; then
                ENV_VARS="$ENV_VARS -e $line"
            fi
        done < "../config/.env"
    fi
    
    docker run -d \
        --name intellidocs-pro \
        -p 8501:8501 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        $ENV_VARS \
        intellidocs-pro:latest
    
    if [ $? -eq 0 ]; then
        print_success "IntelliDocs Pro is running!"
        print_status "Access the application at: http://localhost:8501"
        print_status "Use 'docker stop intellidocs-pro' to stop the application"
    else
        print_error "Failed to start the application"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    
    if docker ps | grep -q intellidocs-pro; then
        docker logs -f intellidocs-pro
    elif docker-compose ps | grep -q intellidocs-pro; then
        cd "$(dirname "$0")"
        docker-compose logs -f
    else
        print_error "IntelliDocs Pro container is not running"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    print_status "Stopping IntelliDocs Pro..."
    
    cd "$(dirname "$0")"
    
    # Try docker-compose first
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
    fi
    
    # Also try stopping standalone container
    if docker ps | grep -q intellidocs-pro; then
        docker stop intellidocs-pro
        docker rm intellidocs-pro
    fi
    
    print_success "IntelliDocs Pro stopped"
}

# Function to show status
show_status() {
    print_status "IntelliDocs Pro Status:"
    
    if docker ps | grep -q intellidocs-pro; then
        print_success "Running (standalone)"
        docker ps | grep intellidocs-pro
    elif docker-compose ps 2>/dev/null | grep -q intellidocs-pro; then
        print_success "Running (docker-compose)"
        cd "$(dirname "$0")"
        docker-compose ps
    else
        print_warning "Not running"
    fi
}

# Main script logic
case "${1:-}" in
    "build")
        print_status "Building IntelliDocs Pro..."
        check_docker
        build_image
        ;;
    "start"|"run")
        print_status "Starting IntelliDocs Pro..."
        check_docker
        if ! check_env_file; then
            exit 1
        fi
        create_directories
        
        if [ -f "$(dirname "$0")/docker-compose.yml" ]; then
            run_compose
        else
            build_image
            run_standalone
        fi
        ;;
    "stop")
        stop_app
        ;;
    "restart")
        stop_app
        sleep 2
        print_status "Restarting..."
        check_docker
        if ! check_env_file; then
            exit 1
        fi
        create_directories
        run_compose
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        echo "IntelliDocs Pro Docker Runner"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  build    Build the Docker image"
        echo "  start    Start the application"
        echo "  stop     Stop the application"
        echo "  restart  Restart the application"
        echo "  logs     Show application logs"
        echo "  status   Show application status"
        echo "  help     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start the application"
        echo "  $0 logs     # View logs"
        echo "  $0 stop     # Stop the application"
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        print_status "Use '$0 help' to see available commands"
        exit 1
        ;;
esac