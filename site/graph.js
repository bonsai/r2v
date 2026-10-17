(() => {
  const $ = s => document.querySelector(s);
  const state = { selected: null, query: '', view: 'list' };
  const modes = ['list', 'graph', 'digest', 'compare'];
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  fetch('./research-map.json').then(r => { if (!r.ok) throw new Error('research data unavailable'); return r.json(); }).then(data => {
    const papers = [...data.seed_papers, ...data.recommended_papers], tags = data.keywords;
    const related = tag => papers.filter(p => p.keywords.includes(tag));
    const list = $('#paper-list'), graph = $('#research-graph'), detail = $('#map-detail'), search = $('#map-search');
    const ns = 'http://www.w3.org/2000/svg';
    const el = (name, attrs) => { const e = document.createElementNS(ns, name); Object.entries(attrs || {}).forEach(([k,v]) => e.setAttribute(k,v)); return e; };
    const queryMatch = p => !state.query || (p.title+' '+p.keywords.join(' ')+' '+(p.why||'')+' '+(p.question||'')).toLowerCase().includes(state.query.toLowerCase());
    const shownPapers = () => papers.filter(p => (!state.selected || p.keywords.includes(state.selected)) && queryMatch(p));
    const shownTags = () => tags.filter(t => (!state.query || (t.id+' '+t.question+' '+related(t.id).map(p=>p.title).join(' ')).toLowerCase().includes(state.query.toLowerCase())) && (!state.selected || t.id===state.selected || related(t.id).some(p=>p.keywords.includes(state.selected))));
    function renderList(shown) {
      list.replaceChildren();
      shown.forEach(p => {
        const a=document.createElement('article'); a.className='paper '+(p.status||'recommended');
        const badge=document.createElement('span'); badge.className='paper-kind'; badge.textContent=p.status==='seed'?'起点論文':'追加候補';
        const h=document.createElement('h3'); const link=document.createElement('a'); link.href=p.url; link.target='_blank'; link.rel='noopener noreferrer'; link.textContent=p.title; h.append(link);
        const why=document.createElement('p'); why.textContent=p.why||'起点となる論文。詳細は原著で確認する。';
        const kw=document.createElement('p'); kw.className='paper-tags'; kw.textContent=p.keywords.join(' · ');
        a.append(badge,h,why,kw); list.append(a);
      });
    }
    function renderGraph(shown, visible) {
      const cloud=$('#tag-cloud'); cloud.replaceChildren();
      visible.slice().sort((a,b)=>b.weight-a.weight||a.id.localeCompare(b.id)).forEach(t=>{
        const b=document.createElement('button'); b.className='tag '+t.kind+(state.selected===t.id?' active':''); b.style.fontSize=(.78+t.weight*.055)+'rem'; b.textContent=t.id; b.title=t.question; b.setAttribute('aria-pressed',String(state.selected===t.id));
        b.addEventListener('click',()=>{state.selected=state.selected===t.id?null:t.id;render();}); cloud.append(b);
      });
      graph.replaceChildren(); const W=940,H=510; graph.setAttribute('viewBox','0 0 '+W+' '+H);
      const visibleTags=visible.slice(0,24), nodes=[];
      visibleTags.forEach((t,i)=>{const angle=-Math.PI/2+i/Math.max(1,visibleTags.length)*Math.PI*2;nodes.push({id:t.id,label:t.id,type:'tag',x:W/2+Math.cos(angle)*185,y:H/2+Math.sin(angle)*180,weight:t.weight});});
      shown.forEach((p,i)=>{const angle=-Math.PI/2+i/Math.max(1,shown.length)*Math.PI*2;nodes.push({id:p.id,label:p.title,type:'paper',paper:p,x:W/2+Math.cos(angle)*365,y:H/2+Math.sin(angle)*225});});
      const pos=Object.fromEntries(nodes.map(n=>[n.id,n]));
      shown.forEach(p=>p.keywords.forEach(k=>{if(pos[p.id]&&pos[k])graph.append(el('line',{x1:pos[p.id].x,y1:pos[p.id].y,x2:pos[k].x,y2:pos[k].y,class:'edge '+(state.selected===k?'edge-hot':'')}));}));
      nodes.forEach(n=>{const g=el('g',{class:'node '+n.type+(state.selected===n.id?' selected':''),tabindex:'0',role:'button','aria-label':n.label});g.append(el('circle',{cx:n.x,cy:n.y,r:n.type==='tag'?4+n.weight*1.5:8,class:'dot'}));const tx=el('text',{x:n.x+12,y:n.y+4,class:'node-label'});tx.textContent=n.type==='tag'?n.label:(n.paper.title.length>34?n.paper.title.slice(0,31)+'…':n.paper.title);g.append(tx);const choose=()=>{if(n.type==='tag'){state.selected=state.selected===n.id?null:n.id;render();}else{window.open(n.paper.url,'_blank','noopener');}};g.addEventListener('click',choose);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose();}});graph.append(g);});
    }
    function renderDigest(shown, visible) {
      const target=$('#digest-panel'); target.replaceChildren();
      const intro=document.createElement('p'); intro.textContent='起点論文 '+data.seed_papers.length+' 本、追加候補 '+data.recommended_papers.length+' 本、研究キーワード '+tags.length+' 件。候補は文献探索のための仮説であり、網羅性や優位性を保証しません。'; target.append(intro);
      const groups=[['中心課題',['identity consistency','multi-reference control','representation alignment']],['制御と失敗',['text controllability','copy-paste artifacts','identity crosstalk','subject binding']],['評価とデータ',['factor-grounded evaluation','benchmark design','training data','data scaling']],['次に広げる領域',['multi-view references','multi-subject generation','training-free methods','keyframe editing','3D consistency']]];
      groups.forEach(([title,ids])=>{const matching=ids.map(id=>tags.find(t=>t.id===id)).filter(t=>t&&visible.includes(t));if(!matching.length)return;const box=document.createElement('article');box.className='digest-card';const h=document.createElement('h3');h.textContent=title;box.append(h);matching.forEach(t=>{const row=document.createElement('p');row.innerHTML='<strong>'+esc(t.id)+'</strong> — '+esc(t.question)+' <span class="muted">('+related(t.id).filter(queryMatch).length+' papers)</span>';box.append(row);});target.append(box);});
      const h=document.createElement('h3');h.textContent='この条件に合う論文';target.append(h);const p=document.createElement('p');p.textContent=shown.map(x=>x.title).join(' / ')||'該当論文なし';target.append(p);
    }
    function renderCompare(shown) {
      const target=$('#compare-panel'); target.replaceChildren();
      const table=document.createElement('table'); table.className='compare-table';
      const header=document.createElement('thead');header.innerHTML='<tr><th>論文</th><th>区分</th><th>年</th><th>主なキーワード</th><th>読む観点</th></tr>';table.append(header);
      const body=document.createElement('tbody');
      shown.forEach(p=>{const tr=document.createElement('tr');const title=document.createElement('td');const a=document.createElement('a');a.href=p.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=p.title;title.append(a);const status=document.createElement('td');status.textContent=p.status==='seed'?'起点':'候補';const year=document.createElement('td');year.textContent=p.year||'—';const kw=document.createElement('td');kw.textContent=p.keywords.join(' · ');const why=document.createElement('td');why.textContent=p.why||'研究の出発点';[title,status,year,kw,why].forEach(td=>tr.append(td));body.append(tr);});
      table.append(body);target.append(table);
    }
    function setView(view, updateUrl=true) {
      state.view=modes.includes(view)?view:'list';
      document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===state.view)));
      modes.forEach(m=>{const panel=$('#'+m+'-view');if(panel)panel.hidden=m!==state.view;});
      if(updateUrl){const u=new URL(window.location.href);u.searchParams.set('view',state.view);history.replaceState(null,'',u);}
      render();
    }
    function render() {
      const shown=shownPapers(), visible=shownTags();
      $('#result-count').textContent=shown.length+' / '+papers.length+' papers · '+visible.length+' keywords';
      renderList(shown); renderGraph(shown,visible); renderDigest(shown,visible); renderCompare(shown);
      detail.textContent=state.selected?'選択中のキーワード: '+state.selected+'。関連する論文と要約・比較を絞り込んでいます。':'List=一覧、Graph=関係探索、Digest=テーマ別要約、Compare=論文比較。検索・キーワード選択は各モードに共通です。';
    }
    document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));
    search.addEventListener('input',()=>{state.query=search.value;render();});
    $('#clear-map').addEventListener('click',()=>{state.selected=null;state.query='';search.value='';render();});
    const requested=new URLSearchParams(window.location.search).get('view')||'list';setView(requested,false);
  }).catch(err=>{$('#map-detail').textContent='研究データを読み込めませんでした: '+err.message;});
})();