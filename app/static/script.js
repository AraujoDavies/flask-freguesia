(async () => { 
    const botoes = document.querySelectorAll(".bi-arrow-clockwise");

    botoes.forEach((botao) => {
        // Faz o efeito de giro ao clicar nos botões de carregamento
        let angulo = 0; 
        botao.addEventListener("click", async () => {
            angulo += 360; 
            botao.style.transform = `rotate(${angulo}deg)`;
            
            // id do botão que foi clicado console.log(botao.id) 

            // Fazendo acao do botao observacao
            if (botao.id == 'observacao') {
                botao.classList.add("nao-clicavel");
                // apagar tela antiga
                const listaDeJogos = document.querySelectorAll(".section-observacao .listar-jogo");
                listaDeJogos.forEach( (jogo, index) => {
                    jogo.remove();
                });
                const sem_dados = document.querySelector(".sem-dados");
                if (sem_dados) {
                    sem_dados.remove();
                }

                // exibir carregamento
                let loading_spinner = document.getElementById("obs-loading");
                loading_spinner.classList.remove('d-none');

                    // montar tela de jogos
                    await fetch(window.urls.rotaObservacao)
                    .then(response => response.json())
                    .then(partidas => {
                        loading_spinner.classList.add('d-none');
                        botao.classList.remove("nao-clicavel");
                        location.reload();
                    });
            }
        });

    });

})();


(async () => { 
    const alertas = document.querySelectorAll('div[role="alert"]');

    alertas.forEach((alerta) => {
        setTimeout(() => {
            alerta.classList.add('fade-out');
            setTimeout(() => alerta.remove(), 500); // espera a animação terminar
        }, 3000);
    });
})();