(() => {
  const $ = s => document.querySelector(s);
  const state = { selected: null, query: '' };
  fetch('./research-map.json').then(r => { if (!r.ok) throw new Error('map unavailable'); return r.json(); }).then(data => {
    const papers = [...data.seed_papers, ...data.recommended_papers], tags = data.keywords;
    const related = tag => papers.filter(p => p.keywords.includes(tag));
    const cloud = $('#tag-cloud'), list = $('#paper-list'), graph = $('#research-graph'), detail = $('#map-detail'), search = $('#map-search');
    const ns = 'http://www.w3.org/2000/svg';
    const el = (name, attrs) => { const e = document.createElementNS(ns, name); Object.entries(attrs || {}).forEach(([k,v]) => e.setAttribute(k,v)); return e; };
    function render() {
      const q = state.query.toLowerCase();
      const visible = tags.filter(t => !q || t.id.toLowerCase().includes(q) || t.question.toLowerCase().includes(q) || related(t.id).some(p => p.title.toLowerCase().includes(q)));
      cloud.replaceChildren();
      visible.slice().sort((a,b) => b.weight-a.weight || a.id.localeCompare(b.id)).forEach(t => {
        const b = document.createElement('button'); b.className = 'tag ' + t.kind + (state.selected===t.id?' active':'');
        b.style.fontSize = (0.78 + t.weight*0.055) + 'rem'; b.textContent=t.id; b.title=t.question; b.setAttribute('aria-pressed',String(state.selected===t.id));
        b.addEventListener('click',()=>{state.selected=state.selected===t.id?null:t.id;render();}); cloud.append(b);
      });
      list.replaceChildren();
      const shown = papers.filter(p => (!state.selected || p.keywords.includes(state.selected)) && (!q || (p.title+' '+p.keywords.join(' ')+' '+(p.why||'')).toLowerCase().includes(q)));
      shown.forEach(p => { const a=document.createElement('article');a.className='paper '+p.status;const badge=document.createElement('span');badge.className='paper-kind';badge.textContent=p.status==='seed'?'起点論文':'追加候補';const h=document.createElement('h3');const link=document.createElement('a');link.href=p.url;link.target='_blank';link.rel='noopener noreferrer';link.textContent=p.title;h.append(link);const why=document.createElement('p');why.textContent=p.why||'起点となる論文。詳細は原著で確認する。';const kw=document.createElement('p');kw.className='paper-tags';kw.textContent=p.keywords.join(' · ');a.append(badge,h,why,kw);list.append(a);});
      $('#result-count').textContent=shown.length+' / '+papers.length+' 論文';
      graph.replaceChildren(); const W=940,H=510;graph.setAttribute('viewBox','0 0 '+W+' '+H);
      const visibleTags=visible.slice(0,24), shownForGraph=papers.filter(p=>!q||(p.title+' '+p.keywords.join(' ')).toLowerCase().includes(q)), nodes=[];
      visibleTags.forEach((t,i)=>{const angle=-Math.PI/2+i/Math.max(1,visibleTags.length)*Math.PI*2;nodes.push({id:t.id,label:t.id,type:'tag',x:W/2+Math.cos(angle)*185,y:H/2+Math.sin(angle)*180,weight:t.weight});});
      shownForGraph.forEach((p,i)=>{const angle=-Math.PI/2+i/Math.max(1,shownForGraph.length)*Math.PI*2;nodes.push({id:p.id,label:p.title,type:'paper',paper:p,x:W/2+Math.cos(angle)*365,y:H/2+Math.sin(angle)*225});});
      const pos=Object.fromEntries(nodes.map(n=>[n.id,n]));
      shownForGraph.forEach(p=>p.keywords.forEach(k=>{if(pos[p.id]&&pos[k])graph.append(el('line',{x1:pos[p.id].x,y1:pos[p.id].y,x2:pos[k].x,y2:pos[k].y,class:'edge '+(state.selected===k?'edge-hot':'')}));}));
      nodes.forEach(n=>{const g=el('g',{class:'node '+n.type+(state.selected===n.id?' selected':''),tabindex:'0',role:'button','aria-label':n.label});g.append(el('circle',{cx:n.x,cy:n.y,r:n.type==='tag'?4+n.weight*1.5:8,class:'dot'}));const tx=el('text',{x:n.x+12,y:n.y+4,class:'node-label'});tx.textContent=n.type==='tag'?n.label:(n.paper.title.length>34?n.paper.title.slice(0,31)+'…':n.paper.title);g.append(tx);const choose=()=>{if(n.type==='tag'){state.selected=state.selected===n.id?null:n.id;render();}else{window.open(n.paper.url,'_blank','noopener');}};g.addEventListener('click',choose);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose();}});graph.append(g);});
      detail.textContent=state.selected?(tags.find(t=>t.id===state.selected)||{}).question||'関連論文を表示中。':'タグを選ぶと関連論文に絞り込み。内側がキーワード、外側が論文。論文ノードをクリックすると原著を開きます。';
    }
    search.addEventListener('input',()=>{state.query=search.value;render();});$('#clear-map').addEventListener('click',()=>{state.selected=null;state.query='';search.value='';render();});render();
  }).catch(err=>{$('#map-detail').textContent='研究マップを読み込めませんでした: '+err.message;});
})();