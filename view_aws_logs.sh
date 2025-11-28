#!/bin/bash

# Script para ver logs del servidor AWS de forma fácil
# Uso: ./view_aws_logs.sh [opcion]
# Opciones: live, api, nginx, files, errors

ELASTIC_IP="3.219.214.103"
SSH_KEY="$HOME/.ssh/voice-agent-key.pem"

show_help() {
    echo "📋 Script para ver logs de AWS"
    echo ""
    echo "Uso: ./view_aws_logs.sh [opcion]"
    echo ""
    echo "Opciones:"
    echo "  live      - Ver logs de la API en tiempo real (CTRL+C para salir)"
    echo "  api       - Ver últimos 50 logs de la API"
    echo "  nginx     - Ver últimos 50 logs de Nginx"
    echo "  files     - Ver logs del archivo app_*.log"
    echo "  errors    - Ver logs de errores del archivo errors_*.log"
    echo "  status    - Ver estado de los contenedores"
    echo ""
    echo "Ejemplos:"
    echo "  ./view_aws_logs.sh live       # Ver logs en tiempo real"
    echo "  ./view_aws_logs.sh api        # Ver últimos logs"
    echo "  ./view_aws_logs.sh errors     # Ver errores"
}

case "$1" in
    live)
        echo "📡 Conectando a logs en tiempo real..."
        echo "   (Presiona CTRL+C para salir)"
        echo ""
        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@$ELASTIC_IP \
            "sudo docker logs -f jess-voice-agent"
        ;;
    
    api)
        echo "📋 Últimos 50 logs de la API:"
        echo ""
        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@$ELASTIC_IP \
            "sudo docker logs --tail 50 jess-voice-agent"
        ;;
    
    nginx)
        echo "🌐 Últimos 50 logs de Nginx:"
        echo ""
        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@$ELASTIC_IP \
            "sudo docker logs --tail 50 jess-nginx"
        ;;
    
    files)
        echo "📄 Logs del archivo app_*.log:"
        echo ""
        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@$ELASTIC_IP \
            "tail -50 ~/voice_agent/logs/app_*.log"
        ;;
    
    errors)
        echo "❌ Logs de errores:"
        echo ""
        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@$ELASTIC_IP \
            "tail -50 ~/voice_agent/logs/errors_*.log 2>/dev/null || echo 'No hay errores registrados'"
        ;;
    
    status)
        echo "📊 Estado de contenedores:"
        echo ""
        ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ec2-user@$ELASTIC_IP \
            "sudo docker ps && echo '' && echo 'Uso de recursos:' && sudo docker stats --no-stream"
        ;;
    
    *)
        show_help
        exit 1
        ;;
esac

