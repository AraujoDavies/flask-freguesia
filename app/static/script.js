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
                        let container = document.querySelector(".section-observacao .base-entradas-bloco-2");

                        partidas.forEach( (partida, index) => {
                            const bloco = document.createElement("div");
                            let rota = window.urls.rotaRecomendar + partida.id

                            bloco.classList.add("listar-jogo")
                            bloco.innerHTML = `
                                <a href="${partida.url}" target="_blank">${partida.evento}</a>
                                <a href="${rota}">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" class="bi bi-arrow-right" viewBox="0 0 16 16">
                                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8"></path>
                                    </svg>
                                </button>
                            `;
                            container.appendChild(bloco)
                        });

                        
                        if (partidas.length == 0) {
                            const bloco = document.createElement("div");
                            bloco.classList.add("sem-dados")
                            bloco.innerHTML = `Sem jogos. Recarregue no botão acima para buscar por novos jogos`
                            container.appendChild(bloco);
                        };
                    });

                loading_spinner.classList.add('d-none');
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