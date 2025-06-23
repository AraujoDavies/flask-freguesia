#!/bin/bash

# Fail fast se algo der errado
set -e

# dar permissão para alterar os .json
sudo chown -R ubuntu:ubuntu .

# Atualiza pacotes e instala dependências
sudo apt update -y
sudo apt install -y python3-pip python3.12-venv nginx
echo "📦 Pacotes atualizados ✅"

# Cria e ativa o ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "🐍 Dependências instaladas no venv ✅"

# Copia o service file para systemd (substituindo variáveis reais se necessário)
sudo cp freguesia.service /etc/systemd/system/freguesia.service
echo "📁 Copiado freguesia.service para systemd ✅"

# Reinicia systemd e serviço do gunicorn
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable freguesia
sudo systemctl restart freguesia
echo "🚀 Serviço 'freguesia' iniciado ✅"

# Copia a config do nginx
sudo cp nginx.conf /etc/nginx/sites-available/freguesia
echo "📁 Copiado nginx.conf para sites-available ✅"

# Cria symlink, se ainda não existir
if [ ! -L /etc/nginx/sites-enabled/freguesia ]; then
  # sudo rm -f /etc/nginx/sites-enabled/default  # Remove o site padrão
  # sudo ln -sf /etc/nginx/sites-available/freguesia /etc/nginx/sites-enabled/
  sudo ln -s /etc/nginx/sites-available/freguesia /etc/nginx/sites-enabled/
  echo "🔗 Symlink para Nginx criado ✅"
fi

# Testa config e reinicia Nginx
sudo nginx -t && sudo systemctl reload nginx
echo "🌐 Nginx recarregado com sucesso ✅"

echo "✅✅ Deploy concluído com sucesso!"
