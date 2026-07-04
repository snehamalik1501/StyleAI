
const state = {
  tab:        'upload',
  outfitB64:  null,
  outfitMime: null,
  inventory:  SERVER_ACCESSORIES || [],
  fullLookSelections:{},
  selectedAccessories:{
    earrings:null,
    necklace:null,
    bracelet:null,
    ring:null,
    handbag:null
},
accessoryMode:{
    earrings:"ai",
    necklace:"ai",
    bracelet:"ai",
    ring:"ai",
    handbag:"ai"
},
  prefs: {
    metal:   (SERVER_PREFS && SERVER_PREFS.metal)          || 'Gold',
    earring: (SERVER_PREFS && SERVER_PREFS.earring_style)  || 'Any',
    style:   (SERVER_PREFS && SERVER_PREFS.styling_level)  || 'Minimal',
    occasion:(SERVER_PREFS && SERVER_PREFS.occasion)       || 'Casual',
    earrings_budget: SERVER_PREFS?.earrings_budget || 500,
earrings_source: SERVER_PREFS?.earrings_source || 'both',

necklace_budget: SERVER_PREFS?.necklace_budget || 1000,
necklace_source: SERVER_PREFS?.necklace_source || 'both',

bracelet_budget: SERVER_PREFS?.bracelet_budget || 700,
bracelet_source: SERVER_PREFS?.bracelet_source || 'both',

ring_budget: SERVER_PREFS?.ring_budget || 500,
ring_source: SERVER_PREFS?.ring_source || 'both',

handbag_budget: SERVER_PREFS?.handbag_budget || 2000,
handbag_source: SERVER_PREFS?.handbag_source || 'both',
  },
  results: null,
  loading: false,
  pendingType: null,
};

const ACC_TYPES = ['Earrings','Necklace','Ring','Bracelet','Handbag'];
const PREF_OPTIONS = {
  metal:   { label:'Metal Preference', opts:['Gold','Silver','Rose Gold','Mixed'] },
  earring: { label:'Earring Style',    opts:['Stud','Hoop','Long/Dangle','Any'] },
  style:   { label:'Styling Level',    opts:['Minimal','Balanced','Statement','Heavy'] },
  occasion:{ label:'Occasion',         opts:['Casual','Office','Party','Wedding','Date Night','Festive'] }
};

function esc(s){ return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

function resizeImg(dataUrl, maxW=800){
  return new Promise(res=>{
    const img=new Image();
    img.onload=()=>{
      const r=Math.min(maxW/img.width,maxW/img.height,1);
      const [w,h]=[Math.round(img.width*r),Math.round(img.height*r)];
      const c=document.createElement('canvas');c.width=w;c.height=h;
      c.getContext('2d').drawImage(img,0,0,w,h);
      res(c.toDataURL('image/jpeg',0.82));
    };
    img.src=dataUrl;
  });
}
function readFile(f){ return new Promise(res=>{const r=new FileReader();r.onload=e=>res(e.target.result);r.readAsDataURL(f);}); }

function setTab(tab) {

    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    document.querySelectorAll('.snav-btn').forEach(btn => {
        btn.classList.remove('on');
    });

    const selectedView = document.getElementById('view-' + tab);
    if (selectedView) {
        selectedView.classList.add('active');
    }

    const selectedBtn = document.querySelector(`[data-tab="${tab}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('on');
    }

    if(tab === 'prefs') renderPrefs();
    if(tab === 'inventory') renderInventory();
    if(t==='upload'){
    renderPrefPills();
    renderAccessorySelectors();
}
    if(tab === 'results') renderResults();
}
const tabs = document.getElementById('tabs');

if(tabs){
    tabs.addEventListener('click',e=>{
        if(e.target.dataset.tab) setTab(e.target.dataset.tab);
    });
}
const dz=document.getElementById('dz');
const outfitFileInput=document.getElementById('outfit-file');
dz.addEventListener('click',(e)=>{
    if(e.target.closest('.studio-upload-btn')) return;
    outfitFileInput.click();
});
dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('over');});
dz.addEventListener('dragleave',()=>dz.classList.remove('over'));
dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('over');handleOutfitFile(e.dataTransfer.files[0]);});
outfitFileInput.addEventListener('change',e=>handleOutfitFile(e.target.files[0]));

async function handleOutfitFile(f){
  if(!f?.type.startsWith('image/')) return;
  const raw=await readFile(f);
  const resized=await resizeImg(raw,800);
  state.outfitB64=resized.split(',')[1];
  state.outfitMime=resized.split(';')[0].slice(5);
  const preview=document.getElementById('outfit-preview');
  preview.src=resized; preview.style.display='block';
  dz.classList.add("has-image");
  document.getElementById('dph').style.display='none';
  dz.classList.add("has-image");
  dz.classList.add('filled');
  document.getElementById('upload-actions').style.display='flex';
}
document.getElementById('remove-outfit').onclick=(e)=>{
  e.stopPropagation();  state.outfitB64=null;state.outfitMime=null;
  document.getElementById('outfit-preview').style.display='none';
  document.getElementById('dph').style.display='block';
  dz.classList.remove('filled');
  document.getElementById('upload-actions').style.display='none';
  outfitFileInput.value='';
};

document.getElementById('analyze-btn').onclick=async(e)=>{
  e.stopPropagation();

  if(!state.outfitB64){
    alert('Please upload an outfit photo first.');
    return;
  }
  state.loading=true; state.results=null;
  setTab('results'); renderResults();
  try{
    const resp=await fetch('/analyze',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
    image_b64: state.outfitB64,
    image_mime: state.outfitMime,
    prefs: state.prefs,
    selected_accessories:
        state.selectedAccessories,
        inventory:  state.inventory.map(i=>({
          id:         i.id,
          type:       i.type,
          image_url:  i.image_url,
          attributes: i.attributes||{}
        })),
      }),
    });
    state.results=await resp.json();
  }catch(e){
    state.results={error:'Something went wrong. Please try again.'};
  }finally{
    state.loading=false;
    renderResults();
    document.getElementById('res-dot').style.display='inline-block';
  }
};

function renderPrefs(){

  const wrap=document.getElementById('prefs-wrap');

  const normalPrefs = `

<div class="prefs-grid">

${Object.entries(PREF_OPTIONS).map(([key,{label,opts}])=>`

<div class="pref-card">

    <p class="ps-label">${esc(label)}</p>

    <div class="opt-row">

        ${opts.map(o=>`

            <button
                class="opt${state.prefs[key]===o?' sel':''}"
                onclick="setPref('${key}','${esc(o)}')">

                ${esc(o)}

            </button>

        `).join('')}

    </div>

</div>

`).join('')}

</div>

`;
  const accessoryPrefs = `
<div class="acc-pref-section">

    ${accessoryCard('earrings','Earrings')}
    ${accessoryCard('necklace','Necklace')}
    ${accessoryCard('bracelet','Bracelet')}
    ${accessoryCard('ring','Ring')}
    ${accessoryCard('handbag','Handbag')}

</div>
`;

  wrap.innerHTML = `
<div class="prefs-layout">

    <div class="prefs-left">
        ${normalPrefs}
    </div>

    <div class="prefs-right">
        ${accessoryPrefs}
    </div>

</div>
`;
}
function accessoryCard(key,label){

  return `
    <div class="acc-pref-card">

      <div class="acc-row-top">

        <h4>${label}</h4>

        <select
          onchange="updateAccessorySource('${key}',this.value)"
        >
          <option value="wardrobe"
            ${state.prefs[`${key}_source`]==='wardrobe'?'selected':''}>
            Wardrobe
          </option>

          <option value="shop"
            ${state.prefs[`${key}_source`]==='shop'?'selected':''}>
            Shop
          </option>

          <option value="both"
            ${state.prefs[`${key}_source`]==='both'?'selected':''}>
            Mix Both
          </option>
        </select>

        <span class="budget-pill">
          ₹ <span id="${key}-budget-value">
            ${state.prefs[`${key}_budget`]}
          </span>
        </span>

      </div>

      <input
        type="range"
        min="100"
        max="5000"
        step="100"
        value="${state.prefs[`${key}_budget`]}"
        oninput="updateAccessoryBudget('${key}',this.value)"
      >

    </div>
  `;
}
async function setPref(key,val){
  state.prefs[key]=val; renderPrefs(); renderPrefPills();
  await fetch('/save-preferences',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(state.prefs)});
}
async function updateAccessorySource(key,value){

  state.prefs[`${key}_source`] = value;

  await fetch('/save-preferences',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(state.prefs)
  });
}

async function updateAccessoryBudget(key,value){

  state.prefs[`${key}_budget`] = parseInt(value);

  const label =
    document.getElementById(`${key}-budget-value`);

  if(label){
    label.textContent = value;
  }

  await fetch('/save-preferences',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(state.prefs)
  });
}

function renderPrefPills(){

  const el =
    document.getElementById('pref-pills-display');

  if(!el) return;

  el.innerHTML = `
    <span class="ppill">${state.prefs.metal}</span>
    <span class="ppill">${state.prefs.earring}</span>
    <span class="ppill">${state.prefs.style}</span>
    <span class="ppill">${state.prefs.occasion}</span>
  `;
}
function renderAccessorySelectors(){

    const container =
        document.getElementById(
            "selected-accessories-panel"
        );

    if(!container) return;

    const categories = [
        "earrings",
        "necklace",
        "bracelet",
        "ring",
        "handbag"
    ];

    container.innerHTML =
        categories.map(category => {

            const items =
    state.inventory.filter(
        item =>
        String(item.type)
        .toLowerCase()
        .trim() === category
    );

            return `
            <div class="fixed-accessory-row">

                <label>
                    ${category}
                </label>

                <div class="choice-row">

                    <button
    class="choice-btn ${
        state.accessoryMode[
            category
        ] === "ai"
        ? "active"
        : ""
    }"
                        onclick="
                            toggleWardrobe(
                                '${category}',
                                false
                            )
                        "
                    >
                        Let AI Decide
                    </button>

                    <button
    class="choice-btn ${
        state.accessoryMode[
            category
        ] === "wardrobe"
        ? "active"
        : ""
    }"
                        onclick="
                            toggleWardrobe(
                                '${category}',
                                true
                            )
                        "
                    >
                        Select From Wardrobe
                    </button>

                </div>

                <div
                    id="wardrobe-${category}"
                    class="wardrobe-choice-grid"
                    style="display:none"
                >

                    ${items.map(item => `

                        <div
                            class="mini-wardrobe-card"
                            onclick="
    selectAccessory(
        '${category}',
        '${item.id}',
        this
    )
"
                        >

                            <img
                                src="${item.image_url}"
                                alt="${item.name}"
                            >

                            <p>
                                ${item.name}
                            </p>

                        </div>

                    `).join("")}

                </div>

            </div>
            `;
        }).join("");
}
renderPrefPills();
function toggleWardrobe(
    category,
    show
){

    const box =
        document.getElementById(
            `wardrobe-${category}`
        );

    if(!box) return;

    box.style.display =
        show ? "grid" : "none";

    state.accessoryMode[
        category
    ] = show
        ? "wardrobe"
        : "ai";

    if(!show){

        state.selectedAccessories[
            category
        ] = null;
    }

    const parent =
        box.closest(
            ".fixed-accessory-row"
        );

    parent
        .querySelectorAll(
            ".choice-btn"
        )
        .forEach(btn =>
            btn.classList.remove(
                "active"
            )
        );

    if(show){

        parent
            .querySelectorAll(
                ".choice-btn"
            )[1]
            .classList.add(
                "active"
            );

    }else{

        parent
            .querySelectorAll(
                ".choice-btn"
            )[0]
            .classList.add(
                "active"
            );
    }
}

function selectAccessory(
    category,
    id,
    element
){

    state.selectedAccessories[
    category
] = element.querySelector("img").getAttribute("src");

    document
        .querySelectorAll(
            `#wardrobe-${category}
             .mini-wardrobe-card`
        )
        .forEach(card => {
            card.classList.remove(
                "selected"
            );
        });

    element.classList.add(
        "selected"
    );

    console.log(
        state.selectedAccessories
    );
}
function renderInventory(){

    const container =
        document.getElementById("wardrobe-sections");

    if(!container) return;

    const grouped = {};

    state.inventory.forEach(item=>{

        const type =
            item.type || "Other";

        if(!grouped[type]){
            grouped[type] = [];
        }

        grouped[type].push(item);
    });

    let html = "";

Object.keys(grouped).forEach(category => {

    html += `
    <div
    class="wardrobe-section"
    id="section-${category}"
>

        <div class="wardrobe-header">

            <div>

                <span class="wardrobe-title">
                    ${category}
                </span>

                <span class="wardrobe-count">
                    (${grouped[category].length})
                </span>

            </div>

        </div>

        <div
            class="wardrobe-row"
            id="row-${category}"
        >
    `;

    grouped[category].forEach(item => {

        html += `
        <div class="wardrobe-card">

            <img
                src="${item.image_url}"
                alt="${item.name || item.type}"
            >

            <div class="wardrobe-info">

                <div class="wardrobe-name">
                    ${item.name || item.type}
                </div>

                <span class="wardrobe-tag">
                    ${item.style || "Accessory"}
                </span>

                <button
                    class="delete-btn"
                    onclick="deleteAcc(${item.id})"
                >
                    ×
                </button>

            </div>

        </div>
        `;
    });

    html += `

        </div>

    </div>
    `;
});
const pills =
document.getElementById("category-pills");

pills.innerHTML = Object.keys(grouped)
.map(cat => `
<button
    class="category-pill"
    onclick="
    document
    .getElementById('section-${cat}')
    .scrollIntoView({
        behavior:'smooth'
    })
">
    ${grouped[cat].length} ${cat}
</button>
`)
.join("");
container.innerHTML = html;
}

async function deleteAcc(id){
  await fetch(`/delete-accessory/${id}`,{method:'DELETE'});
  state.inventory=state.inventory.filter(i=>i.id!==id);
  renderInventory();
}

function openTypePicker(){
  const g=document.getElementById('type-grid');
  g.innerHTML=ACC_TYPES.map(t=>`<button class="tbtn" onclick="pickType('${t}')">${esc(t)}</button>`).join('');
  document.getElementById('modal-type').style.display='flex';
}
function pickType(type){
  state.pendingType=type;
  document.getElementById('modal-type').style.display='none';
  document.getElementById('modal-upload-title').textContent=`Upload photo of your ${type}`;
  document.getElementById('inv-type-input').value=type;
  document.getElementById('modal-upload').style.display='flex';
  document.getElementById('inv-file').value='';
  document.getElementById('inv-filename').textContent='';
  document.getElementById('inv-preview-img').style.display='none';
}

document.getElementById('inv-file').addEventListener('change',async e=>{
  const f=e.target.files[0];
  if(!f) return;
  document.getElementById('inv-filename').textContent=f.name;
  const raw=await readFile(f);
  const prev=document.getElementById('inv-preview-img');
  prev.src=raw; prev.style.display='block';
});
console.log("SUBMIT ACCESSORY CALLED");
async function submitAccessory(){
  const file=document.getElementById('inv-file').files[0];
  if(!file){alert('Please choose a photo first.');return;}
  const btn=document.getElementById('upload-submit-btn');
  btn.textContent='Uploading & recognizing…'; btn.disabled=true;
  const form=new FormData();
  form.append('type',state.pendingType);
  form.append('image',file);
  try{
    const resp=await fetch('/add-accessory',{
    method:'POST',
    body:form
});

console.log("STATUS:", resp.status);

const data=await resp.json();

console.log("DATA:", data);
    if(data.ok){
      state.inventory.push({id:data.id,type:data.type,image_url:data.image_url,attributes:data.attributes||{}});
      closeModals(); renderInventory();
    }
  }finally{
    btn.textContent='Upload'; btn.disabled=false;
  }
}
function closeModals(){
  document.getElementById('modal-type').style.display='none';
  document.getElementById('modal-upload').style.display='none';
}

function renderResults(){
  const el=document.getElementById('results-content');

  if(state.loading){
    el.innerHTML=`

    <div class="lux-loading">

        <div class="lux-loading-card">

            <div class="spin"></div>

            <p class="lux-title">
                Analyzing Your Outfit ✨
            </p>

            <p class="lux-sub">
                Discovering colors, silhouette,
                aesthetic, occasion and perfect accessories
            </p>

            <div class="lux-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>

        </div>

    </div>

    `;
    return;
}

  if(!state.results){
    el.innerHTML=`
      <div class="empty fade">
        <div class="eico">✦</div>
        <p>No results yet</p>
      </div>
    `;
    return;
  }

  if(state.results.error){
    el.innerHTML=`
      <div class="empty fade">
        <div class="eico">!</div>
        <p>${esc(state.results.error)}</p>
      </div>
    `;
    return;
  }

  const r = state.results;
  const categories = [
  ['earrings','Earrings','✨'],
  ['necklace','Necklace','📿'],
  ['bracelet','Bracelet','✨'],
  ['ring','Ring','💍'],
  ['handbag','Handbag','👜']
];

el.innerHTML = `

<div class="recommendation-page">

  <div class="analysis-hero">

      <div class="hero-left">

          <h2>
              Outfit Analysis Complete ✨
          </h2>

          <p class="hero-sub">
              ${r.style || "Elegant Styling"}
          </p>

      </div>

      <div class="hero-right">

          <div class="recommendation-count">

              ${
                categories.reduce(
                  (sum,[key]) =>
                  sum + (r[key]?.length || 0),
                  0
                )
              }

          </div>

          <span>
              Personalized Recommendations
          </span>

      </div>

  </div>

  ${categories.map(([key,label,icon])=>`

      <div class="category-section">

          <div class="category-header">

              <h3>${icon} ${label}</h3>

          </div>

          <div class="recommendation-grid">

          ${(r[key] || []).map(item => `

              <div class="flip-card">

    <div class="flip-card-inner">

        <div class="flip-card-front">

                  <div class="card-top">

    <span class="source-badge ${item.source || 'shop'}">

        ${(item.source || 'shop').toUpperCase()}

    </span>

</div>

                  <img
                      src="${item.image_url || '/static/images/placeholder.jpg'}"
                      class="recommend-img"
                  >

                  <h4>
                      ${item.name || ''}
                  </h4>

                  <p class="card-reason">
    ${(item.reason || '').split('. ')[0]}
</p>

                  ${item.source !== 'wardrobe' && item.budget
? `
<div class="price-row">
    ₹${item.budget}
</div>
`
: ''
}

${item.source === 'wardrobe'
? `

<div class="owned-badge">
    ✓ In Your Wardrobe
</div>

<div class="owned-btn">
    Already Owned
</div>

</div>
</div>
</div>

`

: `

<button
    class="shop-btn"
    onclick="flipCard(this)"
>
    Shop Now →
</button>

</div>

<div class="flip-card-back">

    <h3>Choose Store</h3>

    <a
      class="store-btn amazon"
      href="https://www.amazon.in/s?k=${encodeURIComponent(item.query || item.name || '')}"
      target="_blank">
      Amazon
    </a>

    <a
      class="store-btn flipkart"
      href="https://www.flipkart.com/search?q=${encodeURIComponent(item.query || item.name || '')}"
      target="_blank">
      Flipkart
    </a>

    <a
      class="store-btn myntra"
      href="https://www.myntra.com/${encodeURIComponent(item.query || item.name || '')}"
      target="_blank">
      Myntra
    </a>

    <button
      class="back-btn"
      onclick="flipCard(this)">
      ← Back
    </button>

</div>

</div>
</div>

`
}

`).join('')}

          </div>

      </div>

    `).join('')}

<div class="full-look-builder-section">

    <button
    class="generate-look-btn"
    onclick="openFullLookBuilder()"
>
    ✨ Generate Full Look
</button>
</div>

</div>
`;

}

function flipCard(btn){

    const card =
      btn.closest('.flip-card');

    card.classList.toggle('flipped');

}
function openFullLookBuilder(){

    setTab("full-look");

    const outfit =
        document.getElementById(
            "full-look-outfit"
        );

    const preview =
        document.getElementById(
            "outfit-preview"
        );

    if(outfit && preview){
        outfit.src = preview.src;
    }

    renderFullLookPage();
}
function chooseLookSource(
    category,
    source
){

    if(!state.fullLookSelections){
        state.fullLookSelections = {};
    }

    state.fullLookSelections[
        category
    ] = source;

    console.log(
        state.fullLookSelections
    );
}
function showWardrobeItems(category){

    const items = state.inventory.filter(item =>
        item.type.toLowerCase().trim() === category
    );

    document.getElementById(`content-${category}`).innerHTML = `

    <div
        class="accessory-scroll"
        id="scroll-${category}">

        ${items.map(item => `

            <div
                class="look-wardrobe-card"
                onclick="chooseWardrobeItem(
                    '${category}',
                    '${item.image_url}',
                    this
                )">

                <img src="${item.image_url}">

                <p>${item.name || ""}</p>

            </div>

        `).join("")}

    </div>

    `;
}

async function generateFinalLook(){

    const result =
        await fetch(
            "/generate-full-look",
            {
                method:"POST",
                headers:{
                    "Content-Type":
                    "application/json"
                },
                body:JSON.stringify({

                    outfit:
                        state.results,

                    selections:
                        state.fullLookSelections ||

                        {},

                    wardrobe:
                        state.selectedAccessories

                })
            }
        );

    const data =
        await result.json();

    document.getElementById(
        "final-look-result"
    ).innerHTML = `

        <div class="style-score-card">

            <h2>
                Style Score
            </h2>

            <h1>
                ${data.overall_score}%
            </h1>

            <p>
                Color Harmony:
                ${data.color_harmony}%
            </p>

            <p>
                Occasion Match:
                ${data.occasion_match}%
            </p>

            <p>
                Aesthetic Consistency:
                ${data.aesthetic_consistency}%
            </p>

        </div>

        <div class="feedback-card">

            <h3>
                AI Feedback
            </h3>

            <p>
                ${data.feedback}
            </p>

        </div>

    `;
}
async function generateMoodBoard(){
    const required = [
    "earrings",
    "necklace",
    "bracelet",
    "ring",
    "handbag"
];

for(const category of required){

    if(!state.fullLookSelections[category]){

        alert(
            `Please select a ${category}`
        );

        return;
    }
}

    setTab("mood-board");

    const outfit =
        document.getElementById("outfit-preview").src;

    const getSelected = (category)=>{

        return state.fullLookSelections[category] || "";
    };

    const earrings =
        getSelected("earrings");

    const necklace =
        getSelected("necklace");

    const bracelet =
        getSelected("bracelet");

    const ring =
        getSelected("ring");

    const handbag =
        getSelected("handbag");

    const board =
        document.getElementById(
            "mood-board-container"
        );

    board.innerHTML = `

<div class="complete-look-board">

    <img
        class="board-outfit"
        src="${outfit}"
    >

    ${
        earrings
        ?
        `
        <div class="accessory-card board-earrings">
            <span class="acc-label">Earrings</span>
            <img src="${earrings}">
        </div>
        `
        : ''
    }

    ${
        necklace
        ?
        `
        <div class="accessory-card board-necklace">
            <span class="acc-label">Necklace</span>
            <img src="${necklace}">
        </div>
        `
        : ''
    }

    ${
        bracelet
        ?
        `
        <div class="accessory-card board-bracelet">
            <span class="acc-label">Bracelet</span>
            <img src="${bracelet}">
        </div>
        `
        : ''
    }

    ${
        ring
        ?
        `
        <div class="accessory-card board-ring">
            <span class="acc-label">Ring</span>
            <img src="${ring}">
        </div>
        `
        : ''
    }

    ${
        handbag
        ?
        `
        <div class="accessory-card board-handbag">
            <span class="acc-label">Handbag</span>
            <img src="${handbag}">
        </div>
        `
        : ''
    }

</div>

<div id="final-look-result">
</div>

`;
    generateFinalLook();
}

function renderFullLookPage(){

    const container =
        document.getElementById("full-look-content");

    const categories = [
        "earrings",
        "necklace",
        "bracelet",
        "ring",
        "handbag"
    ];

    container.innerHTML = `

<div class="builder-layout">

    <div class="builder-left">

        <img
            class="builder-outfit"
            src="${document.getElementById("outfit-preview").src}"
        >

    </div>

    <div class="builder-right">

        ${categories.map(cat=>`

        <div class="builder-row">

            <h2>${cat.toUpperCase()}</h2>

            <div class="builder-buttons">

                <button
                    class="look-btn"
                    onclick="showWardrobeItems('${cat}')"
                >
                    My Wardrobe
                </button>

                <button
                    class="look-btn"
                    onclick="showShopUpload('${cat}')"
                >
                    My Shopped Item
                </button>

            </div>

            <div
                id="content-${cat}"
                class="builder-content"
            ></div>

        </div>

        `).join("")}

    </div>

</div>

<div class="builder-bottom">

    <button
        class="generate-final-btn"
        onclick="generateMoodBoard()"
    >
        ✨ Generate Full Look
    </button>

</div>

<div id="final-look-result"></div>

`;
}
function chooseWardrobeItem(
    category,
    image,
    element
){

    state.fullLookSelections[
        category
    ] = image;

    document
    .querySelectorAll(
        `#content-${category} .look-wardrobe-card`
    )
        .forEach(card =>
            card.classList.remove(
                "selected"
            )
        );

    element.classList.add(
        "selected"
    );

    console.log(
        state.fullLookSelections
    );
}
function showShopUpload(category){

    document.getElementById(
        `content-${category}`
    ).innerHTML = `

        <div class="shop-upload-box">

            <input
                type="file"
                accept="image/*"
                onchange="
                    previewShopItem(
                        event,
                        '${category}'
                    )
                "
            >

            <div
                id="preview-${category}"
            ></div>

        </div>

    `;
}
function previewShopItem(
    event,
    category
){

    const file =
        event.target.files[0];

    if(!file) return;

    const reader =
        new FileReader();

    reader.onload = function(e){

        document.getElementById(
            `preview-${category}`
        ).innerHTML = `

            <img
                src="${e.target.result}"
                class="shop-preview-img"
            >

            <p>
                Screenshot Selected ✓
            </p>

        `;

        state.fullLookSelections[
            category
        ] = e.target.result;
    };

    reader.readAsDataURL(file);
}
function newLook(){
  state.outfitB64=null;state.outfitMime=null;state.results=null;
  document.getElementById('outfit-preview').style.display='none';
  document.getElementById('dph').style.display='block';
  dz.classList.remove('filled');
  document.getElementById('upload-actions').style.display='none';
  document.getElementById('outfit-file').value='';
  document.getElementById('res-dot').style.display='none';
  setTab('upload');
}

const _oldSetTab = setTab;
setTab = function(t) {
  if(['lookbook','orders','settings'].includes(t)) return;
  state.tab = t;

  document.querySelectorAll('.snav-btn').forEach(b => b.classList.toggle('on', b.dataset.tab===t));

  const labels = {
    'mood-board':'Mood Board',
    home:'Dashboard',
    upload:'Style Studio',
    inventory:'Wardrobe',
    prefs:'Preferences',
    results:'Recommendations',
    'full-look':'Build Look'
};
  const bc = document.getElementById('topbar-breadcrumb');
  if(bc) bc.textContent = labels[t] || t;

[
'home',
'upload',
'inventory',
'prefs',
'results',
'full-look',
'mood-board'
].forEach(id => {
    const el = document.getElementById('view-'+id);

    if(el){
        el.style.display = (id === t) ? 'block' : 'none';
    }
});

  if(t==='prefs')     renderPrefs();
  if(t==='inventory') renderInventory();
  if(t==='upload'){
    renderPrefPills();
    renderAccessorySelectors();
}
  if(t==='results')   renderResults();
};

document.getElementById('sidebar-nav').addEventListener('click', e => {
  const btn = e.target.closest('.snav-btn');
  if(btn && btn.dataset.tab) setTab(btn.dataset.tab);
});

setTab('home');
function scrollCategory(category){

    const row =
        document.getElementById(
            `row-${category}`
        );

    row.scrollBy({
        left:500,
        behavior:'smooth'
    });

}
const wardrobeSearch = document.getElementById('wardrobe-search');

if(wardrobeSearch){

    wardrobeSearch.addEventListener('input', () => {

        const query =
            wardrobeSearch.value
            .toLowerCase()
            .trim();

        document
            .querySelectorAll('.wardrobe-card')
            .forEach(card => {

                const text =
                    card.textContent.toLowerCase();

                card.style.display =
                    text.includes(query)
                    ? ''
                    : 'none';
            });
    });
}
function scrollAccessories(category,direction){

    const container =
        document.getElementById("scroll-"+category);

    container.scrollBy({

        left:180*direction,

        behavior:"smooth"

    });

}
