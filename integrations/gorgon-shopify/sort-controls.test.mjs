import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const make=(dataset={})=>({dataset,children:[],handlers:{},classList:{toggle(){}},attrs:{},disabled:false,
 addEventListener(t,fn){this.handlers[t]=fn},setAttribute(k,v){this.attrs[k]=v},
 hasAttribute(k){return Object.keys(this.dataset).some(p=>'data-'+p.replace(/[A-Z]/g,c=>'-'+c.toLowerCase())===k)},
 closest(){return this},append(c){this.children.push(c)},replaceChildren(...cs){this.children=cs},focus(){},
 get lastElementChild(){return this.children.at(-1)},querySelector(){return this.children[0]},
 querySelectorAll(){return this.children.flatMap(c=>c.children||[])}
});
const panel=make(),scene=make(), map={};
const keys=['operation','criteria','variants','add-variant','proceed','criteria-status','run','download','chain','folder-title','folder-status','slide','position','picker'];
for(const k of keys)map['[data-frogger-'+k+']']=make({['frogger'+k.split('-').map(x=>x[0].toUpperCase()+x.slice(1)).join('')]:''});
for(const [k,v] of [['folder','source'],['slide-by','-1'],['slide-by','1']])map['[data-frogger-'+k+'="'+v+'"]']=make();
const tabs=Array.from({length:4},(_,i)=>make({froggerStep:String(i)}));
panel.querySelector=s=>map[s];panel.querySelectorAll=s=>s==='[data-frogger-step]'?tabs:[];
scene.querySelectorAll=()=>[panel];
let connects=0,disposed=0,health=0;
const window={GorgonConnections:{create:()=>({async connect(){connects++},async request(){health++},dispose(){disposed++}})}};
vm.runInNewContext(fs.readFileSync(fileURLToPath(new URL('./gorgon-frogger.js',import.meta.url)),'utf8'),{window,document:{querySelectorAll:()=>[scene],createElement:()=>make()}});
const click=k=>panel.handlers.click({target:map['[data-frogger-'+k+']']});
const input=(index,value)=>{const el=map['[data-frogger-variants]'].children[index].children[0];el.value=value;panel.handlers.input({target:el})};
map['[data-frogger-operation]'].handlers.change({target:{value:'sort'}});
await click('proceed');assert.match(map['[data-frogger-folder-status]'].textContent,/valid/);
input(0,'Navy Blue');await click('add-variant');input(1,'Olive Green');await click('proceed');
assert.match(map['[data-frogger-criteria-status]'].textContent,/Ready: Navy Blue, Olive Green/);
assert.equal(map['[data-frogger-run]'].disabled,true);
const command=async command=>scene.handlers['gorgon-command']({detail:{command,report(){}}});
await command('Start');assert.equal(connects,1);assert.equal(map['[data-frogger-run]'].disabled,false);
await command('Diagnose');assert.equal(health,1);
input(1,'navy blue');await click('proceed');assert.match(map['[data-frogger-folder-status]'].textContent,/different/);assert.equal(map['[data-frogger-run]'].disabled,true);
input(1,'Olive Green');await click('proceed');await command('Stop');assert.equal(disposed,1);assert.equal(map['[data-frogger-run]'].disabled,true);
await command('Restart');assert.equal(connects,2);assert.equal(map['[data-frogger-run]'].disabled,false);
console.log('Passed variant add/proceed/duplicate validation, edit invalidation, and Start/Stop/Restart/Diagnose connectivity.');
