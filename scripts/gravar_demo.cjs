// Opcional: npm install --no-save playwright; navegador Chrome instalado.
// Instalar também o encoder: npx playwright install ffmpeg
// Grava interações reais do app local e adiciona explicações visíveis na tela.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const root = path.resolve(__dirname, '..');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 },
    recordVideo: { dir: path.join(root, '.cache/video'), size: { width: 1280, height: 900 } } });
  const page = await context.newPage();
  const timeline = [];
  const inicio = Date.now();
  async function legenda(texto, segundos) {
    await page.evaluate(text => {
      let e = document.getElementById('legenda-gravacao');
      if (!e) {
        e = document.createElement('div'); e.id = 'legenda-gravacao';
        e.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:999999;background:#183347;color:white;padding:22px 48px;font:24px/1.45 Arial,sans-serif;border-top:4px solid #176C78;min-height:90px;box-sizing:border-box;pointer-events:none;';
        document.body.appendChild(e);
      }
      e.textContent = text;
    }, texto);
    timeline.push({ inicio_segundos: (Date.now()-inicio)/1000, duracao_planejada: segundos, texto });
    console.log(texto);
    await page.waitForTimeout(segundos*1000);
  }
  const nav = async texto => {
    await page.getByText(texto, {exact:true}).first().click();
    await page.waitForTimeout(600);
    await page.locator('section.main, [data-testid="stMain"]').first().evaluate(e=>e.scrollTop=0).catch(()=>{});
  };
  try {
    await page.goto('http://127.0.0.1:8502');
    await page.getByRole('heading',{name:'Analisar um relato',exact:true}).waitFor();
    await page.addStyleTag({content: '.block-container { padding-bottom: 190px !important; }'});
    await nav('Sobre o projeto');
    await legenda('CardioIA · Guilherme Yamada Dantas · RM 568506. Demonstração acadêmica da Fase 2, com dados fictícios e sem uso assistencial.',15);
    await nav('Dez relatos');
    await legenda('Parte 1: dez relatos completos descrevem sintomas, início e efeito na rotina. Cada hipótese mostra as expressões que acionaram a regra.',18);
    await page.getByRole('heading',{name:'Mapa de conhecimento',exact:true}).evaluate(e => e.scrollIntoView({block:"center"}));
    await legenda('O CSV associa dois sintomas a uma hipótese didática. Essas combinações não são critérios diagnósticos validados e não confirmam doenças.',16);
    await nav('Analisar relato');
    await page.getByRole('textbox',{name:'Relato fictício'}).fill('Desde esta manhã sinto dor no peito e suor frio, e precisei interromper meu trabalho.');
    await page.getByRole('button',{name:'Analisar relato',exact:true}).click();
    await page.getByRole('heading',{name:'O que as regras encontraram'}).evaluate(e => e.scrollIntoView({block:"center"}));
    await legenda('A extração reconhece expressões afirmadas. À direita, o classificador aprende um rótulo a partir de exemplos: são duas abordagens distintas.',18);
    await page.getByRole('textbox',{name:'Relato fictício'}).fill('Não sinto dor no peito e não tenho suor frio.');
    await page.getByRole('button',{name:'Analisar relato',exact:true}).click();
    await page.getByRole('heading',{name:'O que as regras encontraram'}).evaluate(e => e.scrollIntoView({block:"center"}));
    await legenda('Contraexemplo: as regras reconhecem a negação, mas o modelo ainda prevê alto risco. A falha linguística é exibida, não ocultada pelas métricas.',20);
    await page.getByRole('textbox',{name:'Relato fictício'}).fill('xyzk qwrtyp');
    await page.getByRole('button',{name:'Analisar relato',exact:true}).click();
    await page.getByRole('heading',{name:'O que as regras encontraram'}).evaluate(e => e.scrollIntoView({block:"center"}));
    await legenda('Sem vocabulário conhecido, o classificador se abstém. Mesmo quando conhece palavras, ainda pode errar o contexto.',12);
    await nav('Avaliação');
    await legenda('Parte 2: 160 frases sintéticas, divididas por cenário em 96 para treino, 32 para validação e 32 para teste. Paráfrases ficam na mesma partição.',18);
    await page.getByRole('heading',{name:'Matriz de confusão',exact:true}).evaluate(e => e.scrollIntoView({block:"center"}));
    await legenda('Teste: 32 acertos e baseline de 50%. Validação: 75%. Os conjuntos são pequenos e artificiais; os resultados não medem desempenho em pacientes.',18);
    await page.getByRole('heading',{name:'O teste perfeito não encerra a análise',exact:true}).evaluate(e => e.scrollIntoView({block:"center"}));
    await legenda('A sondagem posterior mostra previsões para afirmações e negações. Não foi usada para reajustar o modelo e não tem rótulos clínicos validados.',20);
    await page.getByText('Protocolo e versões',{exact:true}).click();
    await page.getByText('Protocolo e versões',{exact:true}).evaluate(e => e.scrollIntoView({block:"center"}));
    await legenda('TF-IDF aprende apenas no treino. Regressão logística usa parâmetros fixos. Os notebooks salvam versões, partições, matriz de confusão e previsões.',17);
    await nav('Sobre o projeto');
    await legenda('Os arquivos incluem testes, documentação e instruções de reprodução. Um uso médico exigiria dados adequados, revisão clínica e validação externa.',16);
    await legenda('CardioIA Fase 2 · Guilherme Yamada Dantas · RM 568506. Resultado acadêmico reproduzível, com limitações explícitas.',8);
  } finally {
    const video = page.video();
    await context.close();
    const destino = path.join(root,'.cache/video/cardioia-demo.webm');
    await video.saveAs(destino);
    fs.mkdirSync(path.join(root,'document/video'),{recursive:true});
    fs.writeFileSync(path.join(root,'document/video/sequencia.json'),JSON.stringify(timeline,null,2));
    await browser.close();
    console.log('Vídeo bruto:',destino);
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
