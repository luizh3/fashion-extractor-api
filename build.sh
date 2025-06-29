#!/bin/bash

# Script para build e execução da API CLIP
echo "🚀 Iniciando build da API CLIP & Body Parts..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cores
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

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose não encontrado. Tentando usar 'docker compose'..."
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose."
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Criar diretórios necessários
print_status "Criando diretórios necessários..."
mkdir -p logs
mkdir -p test_images

# Build da imagem
print_status "Construindo imagem Docker..."
if $COMPOSE_CMD build --no-cache; then
    print_success "Imagem construída com sucesso!"
else
    print_error "Erro ao construir imagem Docker."
    exit 1
fi

# Executar container
print_status "Iniciando container..."
if $COMPOSE_CMD up -d; then
    print_success "Container iniciado com sucesso!"
    echo ""
    print_status "📋 Informações da API:"
    echo "   🌐 URL: http://localhost:8000"
    echo "   📚 Docs: http://localhost:8000/docs"
    echo "   ❤️  Health: http://localhost:8000/health"
    echo ""
    print_status "📊 Para ver os logs:"
    echo "   $COMPOSE_CMD logs -f clip-api"
    echo ""
    print_status "🛑 Para parar:"
    echo "   $COMPOSE_CMD down"
    echo ""
    print_warning "⏳ Aguarde alguns segundos para os modelos carregarem..."
    print_status "Verificando status da API..."
    
    # Aguardar API ficar pronta
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "API está pronta! 🎉"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "API pode estar demorando para carregar os modelos..."
            print_status "Verifique os logs com: $COMPOSE_CMD logs clip-api"
        fi
        sleep 2
    done
    
else
    print_error "Erro ao iniciar container."
    exit 1
fi 