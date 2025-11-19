#!/bin/bash

# sherpa-worktree.sh
# Script para crear ramas usando gh-sherpa en git worktrees y navegar automáticamente
# Con soporte para limpiar worktrees
# Uso: ./sherpa-worktree.sh --issue JIRA-123 [OPTIONS]
#      ./sherpa-worktree.sh --clean [WORKTREE_NAME]
#      ./sherpa-worktree.sh --list

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Variables
ISSUE=""
BASE_BRANCH=""
NO_FETCH=false
PREFER_HOTFIX=false
NO_CD=false
CLEAN_MODE=false
LIST_MODE=false
CLEAN_TARGET=""
WORKTREE_PATH=""
BRANCH_NAME=""

# Función para mostrar ayuda
show_help() {
    cat << EOF
${BLUE}🧭 Sherpa Worktree - Gestiona git worktrees con gh-sherpa${NC}

${GREEN}Uso:${NC}
    ${CYAN}# Crear worktree${NC}
    ./sherpa-worktree.sh --issue ISSUE_ID [OPTIONS]

    ${CYAN}# Limpiar worktree${NC}
    ./sherpa-worktree.sh --clean [WORKTREE_NAME]
    ./sherpa-worktree.sh --clean  ${YELLOW}# Modo interactivo${NC}

    ${CYAN}# Listar worktrees${NC}
    ./sherpa-worktree.sh --list

${GREEN}Opciones para crear worktree:${NC}
    --issue, -i ISSUE_ID        ID de la issue (ej: JIRA-123, 456)
    --base, -b BRANCH           Rama base (default: rama principal)
    --no-fetch                  No hace fetch a ramas remotas
    --prefer-hotfix             Prefiere rama hotfix para bugs
    --no-cd                     No navega al worktree

${GREEN}Opciones para limpiar:${NC}
    --clean [NAME]              Elimina un worktree específico o interactivo
    --clean-all                 Elimina TODOS los worktrees (⚠️  cuidado!)
    --list, -l                  Lista todos los worktrees activos

${GREEN}Ejemplos:${NC}
    ${CYAN}# Crear${NC}
    ./sherpa-worktree.sh --issue JIRA-123
    ./sherpa-worktree.sh -i JIRA-456 --base develop
    
    ${CYAN}# Limpiar${NC}
    ./sherpa-worktree.sh --clean
    ./sherpa-worktree.sh --clean feature/jira-123-descripcion
    ./sherpa-worktree.sh --clean-all
    
    ${CYAN}# Listar${NC}
    ./sherpa-worktree.sh --list

${GREEN}Ayuda:${NC}
    ./sherpa-worktree.sh --help

EOF
}

# Función para listar worktrees
list_worktrees() {
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}📋 Worktrees activos${NC}"
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    
    local worktrees_found=false
    
    if git worktree list --porcelain | grep -q '^worktree'; then
        worktrees_found=true
        
        git worktree list --porcelain | while IFS= read -r line; do
            if [[ $line == worktree* ]]; then
                local worktree_path=$(echo "$line" | cut -d' ' -f2)
                local worktree_name=$(basename "$worktree_path")
                
                # Obtener rama asociada
                if [[ -d "$worktree_path" ]]; then
                    local branch_name=$(cd "$worktree_path" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "desconocida")
                    echo -e "  ${GREEN}✓${NC} ${CYAN}$worktree_name${NC}"
                    echo -e "    📂 Ruta: ${YELLOW}$worktree_path${NC}"
                    echo -e "    🌿 Rama: ${GREEN}$branch_name${NC}"
                    echo ""
                fi
            fi
        done
    else
        echo -e "${YELLOW}ℹ No hay worktrees activos${NC}"
    fi
    
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
}

# Función para limpiar worktrees de forma interactiva
clean_worktrees_interactive() {
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}🧹 Limpiar worktrees${NC}"
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    
    local worktrees=()
    
    # Recopilar worktrees
    while IFS= read -r line; do
        if [[ $line == worktree* ]]; then
            local worktree_path=$(echo "$line" | cut -d' ' -f2)
            local worktree_name=$(basename "$worktree_path")
            worktrees+=("$worktree_path|$worktree_name")
        fi
    done < <(git worktree list --porcelain)
    
    if [ ${#worktrees[@]} -eq 0 ]; then
        echo -e "${YELLOW}ℹ No hay worktrees para limpiar${NC}"
        return 0
    fi
    
    echo -e "${CYAN}Worktrees disponibles:${NC}"
    local i=1
    for worktree in "${worktrees[@]}"; do
        local path=$(echo "$worktree" | cut -d'|' -f1)
        local name=$(echo "$worktree" | cut -d'|' -f2)
        echo -e "  ${YELLOW}$i)${NC} $name ${BLUE}($path)${NC}"
        ((i++))
    done
    
    echo ""
    read -p "Selecciona el número del worktree a eliminar (o Enter para cancelar): " selection
    
    if [ -z "$selection" ]; then
        echo -e "${YELLOW}✗ Cancelado${NC}"
        return 0
    fi
    
    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#worktrees[@]} ]; then
        echo -e "${RED}❌ Selección inválida${NC}"
        return 1
    fi
    
    local selected_worktree=${worktrees[$((selection-1))]}
    local path=$(echo "$selected_worktree" | cut -d'|' -f1)
    local name=$(echo "$selected_worktree" | cut -d'|' -f2)
    
    echo -e "${YELLOW}⚠️  Vas a eliminar: ${CYAN}$name${NC}"
    read -p "¿Estás seguro? (s/N): " confirm
    
    if [[ ! "$confirm" =~ ^[sS]$ ]]; then
        echo -e "${YELLOW}✗ Cancelado${NC}"
        return 0
    fi
    
    # Volver al directorio principal si estamos en el worktree
    if [ "$PWD" = "$path" ] || [[ "$PWD" == "$path"/* ]]; then
        echo -e "${YELLOW}📍 Volviendo al repositorio principal...${NC}"
        cd ..
        while [[ "$(pwd)" == *".worktrees"* ]]; do
            cd ..
        done
        echo -e "${GREEN}✓ De vuelta en el repositorio principal${NC}"
    fi
    
    # Eliminar worktree
    if git worktree remove "$path" 2>/dev/null || git worktree remove --force "$path" 2>/dev/null; then
        echo -e "${GREEN}✓ Worktree eliminado: ${CYAN}$name${NC}"
        
        # Intentar eliminar directorio vacío
        if [ -d "$path" ]; then
            rm -rf "$path" 2>/dev/null || true
        fi
        
        echo -e "${GREEN}✓ ¡Limpieza completada!${NC}"
    else
        echo -e "${RED}❌ Error al eliminar el worktree${NC}"
        return 1
    fi
}

# Función para limpiar worktree específico
clean_specific_worktree() {
    local target_name="$1"
    local target_path=".worktrees/$target_name"
    
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}🧹 Eliminar worktree${NC}"
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    
    # Buscar el worktree
    local found=false
    local full_path=""
    
    while IFS= read -r line; do
        if [[ $line == worktree* ]]; then
            local wt_path=$(echo "$line" | cut -d' ' -f2)
            local wt_name=$(basename "$wt_path")
            
            if [[ "$wt_name" == "$target_name" ]] || [[ "$wt_path" == "$target_path" ]]; then
                found=true
                full_path="$wt_path"
                break
            fi
        fi
    done < <(git worktree list --porcelain)
    
    if [ "$found" = false ]; then
        echo -e "${RED}❌ Worktree no encontrado: $target_name${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🗑️  Eliminando: ${CYAN}$(basename $full_path)${NC}"
    
    # Volver al principal si estamos dentro
    if [ "$PWD" = "$full_path" ] || [[ "$PWD" == "$full_path"/* ]]; then
        echo -e "${YELLOW}📍 Volviendo al repositorio principal...${NC}"
        cd ..
        while [[ "$(pwd)" == *".worktrees"* ]]; do
            cd ..
        done
        echo -e "${GREEN}✓ De vuelta en el repositorio principal${NC}"
    fi
    
    # Eliminar
    if git worktree remove "$full_path" 2>/dev/null || git worktree remove --force "$full_path" 2>/dev/null; then
        [ -d "$full_path" ] && rm -rf "$full_path" 2>/dev/null || true
        echo -e "${GREEN}✓ Worktree eliminado exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al eliminar worktree${NC}"
        return 1
    fi
}

# Función para limpiar todos los worktrees
clean_all_worktrees() {
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    echo -e "${RED}⚠️  ELIMINARÁ TODOS LOS WORKTREES${NC}"
    echo -e "${BLUE}════════════════════════════════════════════${NC}"
    
    read -p "¿Estás completamente seguro? Escribe 'SÍ' para confirmar: " confirm
    
    if [[ "$confirm" != "SÍ" ]]; then
        echo -e "${YELLOW}✗ Cancelado${NC}"
        return 0
    fi
    
    local count=0
    while IFS= read -r line; do
        if [[ $line == worktree* ]]; then
            local wt_path=$(echo "$line" | cut -d' ' -f2)
            
            # Volver si estamos dentro
            if [ "$PWD" = "$wt_path" ] || [[ "$PWD" == "$wt_path"/* ]]; then
                cd ..
                while [[ "$(pwd)" == *".worktrees"* ]]; do
                    cd ..
                done
            fi
            
            git worktree remove "$wt_path" 2>/dev/null || git worktree remove --force "$wt_path" 2>/dev/null
            [ -d "$wt_path" ] && rm -rf "$wt_path" 2>/dev/null || true
            ((count++))
        fi
    done < <(git worktree list --porcelain)
    
    # Limpiar directorio .worktrees si está vacío
    [ -d ".worktrees" ] && rmdir ".worktrees" 2>/dev/null || true
    
    echo -e "${GREEN}✓ Se eliminaron $count worktrees${NC}"
}

# Parsing de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --issue|-i)
            ISSUE="$2"
            shift 2
            ;;
        --base|-b)
            BASE_BRANCH="$2"
            shift 2
            ;;
        --no-fetch)
            NO_FETCH=true
            shift
            ;;
        --prefer-hotfix)
            PREFER_HOTFIX=true
            shift
            ;;
        --no-cd)
            NO_CD=true
            shift
            ;;
        --clean)
            CLEAN_MODE=true
            CLEAN_TARGET="$2"
            shift 2 || shift
            ;;
        --clean-all)
            clean_all_worktrees
            exit 0
            ;;
        --list|-l)
            LIST_MODE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Error: Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Ejecutar según modo
if [ "$LIST_MODE" = true ]; then
    list_worktrees
    exit 0
fi

if [ "$CLEAN_MODE" = true ]; then
    if [ -z "$CLEAN_TARGET" ]; then
        clean_worktrees_interactive
    else
        clean_specific_worktree "$CLEAN_TARGET"
    fi
    exit $?
fi

# Modo crear (por defecto)
if [ -z "$ISSUE" ]; then
    echo -e "${RED}❌ Error: Debes especificar un --issue${NC}"
    show_help
    exit 1
fi

# Verificar que estamos en un repositorio git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: No estamos en un repositorio git${NC}"
    exit 1
fi

# Verificar que gh-sherpa está instalado
if ! gh sherpa --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: gh-sherpa no está instalado${NC}"
    echo -e "${YELLOW}ℹ Instálalo con: gh extension install InditexTech/gh-sherpa${NC}"
    exit 1
fi

# Obtener rama base
if [ -z "$BASE_BRANCH" ]; then
    BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
    echo -e "${CYAN}ℹ Rama base detectada: ${GREEN}$BASE_BRANCH${NC}"
fi

# Construir comando de sherpa
SHERPA_CMD="gh sherpa create-branch --issue $ISSUE --base $BASE_BRANCH --yes"

if [ "$NO_FETCH" = true ]; then
    SHERPA_CMD="$SHERPA_CMD --no-fetch"
fi

if [ "$PREFER_HOTFIX" = true ]; then
    SHERPA_CMD="$SHERPA_CMD --prefer-hotfix"
fi

echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}📦 Sherpa Worktree${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${CYAN}Issue:${NC} ${GREEN}$ISSUE${NC}"
echo -e "${CYAN}Rama base:${NC} ${GREEN}$BASE_BRANCH${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"

# Ejecutar sherpa para crear la rama
echo -e "${YELLOW}📌 Creando rama con sherpa...${NC}"
if ! eval "$SHERPA_CMD"; then
    echo -e "${RED}❌ Error al crear la rama con sherpa${NC}"
    exit 1
fi

# Obtener el nombre de la rama creada
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

echo -e "${GREEN}✓ Rama creada: ${CYAN}$BRANCH_NAME${NC}"

# Crear worktree
WORKTREE_PATH=".worktrees/$BRANCH_NAME"

echo -e "${YELLOW}📂 Creando worktree en: ${CYAN}$WORKTREE_PATH${NC}"

# Crear directorio si no existe
mkdir -p .worktrees

# Crear el worktree
if git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"; then
    echo -e "${GREEN}✓ Worktree creado exitosamente${NC}"
else
    echo -e "${RED}❌ Error al crear el worktree${NC}"
    exit 1
fi

# Mostrar información final
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ ¡Todo listo!${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"

# Navegar al worktree si no está deshabilitado
if [ "$NO_CD" = false ]; then
    echo -e "${YELLOW}🚀 Navegando al worktree...${NC}"
    echo -e "${CYAN}cd $WORKTREE_PATH${NC}"
    cd "$WORKTREE_PATH"
    echo -e "${GREEN}✓ ¡Ya estás en el worktree!${NC}"
    echo -e ""
    echo -e "${CYAN}📍 Ubicación actual:${NC}"
    pwd
    echo -e ""
else
    echo -e "${YELLOW}ℹ Modo --no-cd activado. No navegaste al worktree.${NC}"
    echo -e "${CYAN}Para entrar, ejecuta:${NC}"
    echo -e "  ${GREEN}cd $WORKTREE_PATH${NC}"
    echo -e ""
fi

# Mostrar instrucciones finales
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${YELLOW}📋 Próximos pasos:${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "  1. ${CYAN}Haz tus cambios:${NC}"
echo -e "     editor archivo.ts"
echo -e ""
echo -e "  2. ${CYAN}Commitea y pushea:${NC}"
echo -e "     ${GREEN}git add .${NC}"
echo -e "     ${GREEN}git commit -m 'Implementar $ISSUE'${NC}"
echo -e "     ${GREEN}git push${NC}"
echo -e ""
echo -e "  3. ${CYAN}Crea el PR:${NC}"
echo -e "     ${GREEN}gh sherpa create-pr --issue $ISSUE --yes --no-draft${NC}"
echo -e ""
echo -e "  4. ${CYAN}Cuando termines, limpia el worktree:${NC}"
echo -e "     ${GREEN}../../../sherpa-worktree.sh --clean${NC}"
echo -e "     ${YELLOW}o${NC}"
echo -e "     ${GREEN}cd ../.. && ./sherpa-worktree.sh --clean${NC}"
echo -e ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
