import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const skill = '/Users/yuhaiyang/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.51657/skills/presentations';
const runtimePython = '/Users/yuhaiyang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const data = JSON.parse(await fs.readFile(path.join(root,'assets/colab-results.json'),'utf8'));
const r=data.runs, m=data.metadata, b=r['Adam 0.001'];
const fmt=x=>Number(x).toFixed(2), loss=x=>Number(x).toFixed(4);
const C={ink:'#172C3C', muted:'#546574', teal:'#007F78', blue:'#2864A5', red:'#BC4D39', orange:'#C77D24', paper:'#FAFAF6', pale:'#E8EFEE', line:'#CCD6D7',white:'#FFFFFF'};
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const speaking=[];
function box(s,x,y,w,h,fill){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});}
function text(s,value,x,y,w,h,size=28,color=C.ink,bold=false){const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=value;a.text.style={typeface:'Arial',fontSize:size,color,bold};return a;}
function slide(title,time,cues,source='Colab export, 18 October 2026. Seed 42. Local assets/colab-results.json.'){
 const s=pres.slides.add(); s.background.fill=C.paper;
 text(s,title,64,42,1150,100,43,C.ink,true);
 const n=pres.slides.items.length;
 text(s,n<=12?String(n).padStart(2,'0'):('B'+(n-12)),1160,665,64,28,19,C.muted);
 s.speakerNotes.text=`${time}\n\n${cues}\n\nSource: ${source}`;
 speaking.push({slide:n,title,time,cues,source});return s;
}
async function pic(s,name,x,y,w,h){const bytes=await fs.readFile(path.join(root,'assets',name));s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:name.replaceAll('-',' '),fit:'contain',position:{left:x,top:y,width:w,height:h}});}
function table(s,values,x,y,w,h,widths,size=24){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.borders.assign({fill:C.line,width:1,style:'solid'});
 for(let i=0;i<values.length;i++) for(let j=0;j<values[0].length;j++){
  const c=t.getCell(i,j);c.fill=i===0?C.ink:(i%2===0?C.pale:C.white);c.text.style={typeface:'Arial',fontSize:size,color:i===0?C.white:C.ink,bold:i===0};
 }
 return t;
}
// 1. Cover
{
const s=pres.slides.add();s.background.fill=C.ink;
text(s,'IoT Network Attack Detection\nUsing Neural Networks',68,145,1130,190,60,C.white,true);
text(s,'I organised the full pipeline and focused on training experiments',72,377,1090,72,30,'#82D1C5');
text(s,'Yang Yu\nCSIP5103D   /   21 October 2026',72,545,1000,80,25,'#D9E4E7');
s.speakerNotes.text='0:20\n\nOur question: normal or attack?\nMy part: full pipeline; training settings\nToday: what changed; what I learned\n\nSource: ../presentation-plan.md, personal contribution confirmed by user.';
speaking.push({slide:1,title:'IoT Network Attack Detection Using Neural Networks',time:'0:20',cues:'Normal or attack? / My part: full pipeline + training / What changed; what I learned'});
}
// 2
{
const s=slide('We need to catch attacks and avoid false alarms','1:00','Think of a smoke alarm / 烟雾报警器\nFire, no alarm: missed attack\nNo fire, alarm: false alarm\nAim: classify IoT traffic\nObjectives: build; compare; evaluate','Project scope and evaluation definitions in notebooks/iot_attack_detection.ipynb, test_model.');
table(s,[['Real traffic','Model says normal','Model says attack'],['Normal','Correct','False alarm'],['Attack','Missed attack','Correct']],80,190,1120,240,[280,420,420],30);
text(s,'Aim: recognise normal and attack traffic with an MLP',80,485,1120,42,30,C.teal,true);
text(s,'Build a repeatable pipeline. Compare training settings. Measure both mistakes.',80,550,1100,75,27);
}
// 3
{
const s=slide('We study training choices on an IoT dataset','0:50','Dataset paper: autoencoder; edge resources\nBackpropagation: calculate gradients\nAdam: adapt updates\nOur question: training choices; missed attacks; false alarms','Sharmila & Nagapadma (2023), https://doi.org/10.1186/s42400-023-00178-5\nRumelhart, Hinton & Williams (1986), https://doi.org/10.1038/323533a0\nKingma & Ba (2015), https://arxiv.org/abs/1412.6980');
table(s,[['Study','Main idea','How we use it'],['Sharmila & Nagapadma, 2023','Quantised autoencoder for IoT edge devices','RT-IoT2022 data'],['Rumelhart et al., 1986','Backpropagation','Calculate gradients'],['Kingma & Ba, 2015','Adam optimiser','Compare training updates']],64,175,1152,330,[340,470,342],25);
text(s,'Our focus: a supervised MLP and controlled training experiments',70,559,1120,70,31,C.teal,true);
}
// 4
{
const s=slide('About 90% of the records are attacks','0:50','Raw: 123,117 flows; 83 features\nAfter cleaning: 117,922 flows\nAlways say attack: about 90% accuracy\nSo: detection rate AND false alarms','Colab metadata counts and raw_rows. Dataset: https://archive.ics.uci.edu/dataset/942/rt-iot2022. Counts refer to the project CSV after cleaning.');
await pic(s,'class-balance.png',62,150,850,450);
text(s,'123,117',935,195,290,70,49,C.ink,true);text(s,'raw flows',940,270,260,40,25,C.muted);
text(s,'117,922',935,350,290,70,49,C.teal,true);text(s,'after cleaning',940,425,260,40,25,C.muted);
text(s,'Accuracy alone hides the false alarms',75,611,1100,48,30,C.red,true);
}
// 5
{
const s=slide('I connected cleaning, training and evaluation','1:10','My part: organised implementation; one notebook\nClean before split\nTrain 70%; validation 15%; test 15%\nFit scaler on training rows only\nSame split and seed\nHonest limit: panel shows test metrics after each run','Project notebook Steps 1–7; Colab metadata. Current run_experiment calls test_model after every experiment. Validation chooses early-stopping weights; the test was visible during exploration, so it is not an untouched final benchmark.');
const xs=[70,455,840], ys=[190,405];
[['1  Clean','Remove duplicates'],['2  Split','70% / 15% / 15%'],['3  Scale','Fit on train only'],['4  Train','MLP + optimiser'],['5  Validate','Keep best weights'],['6  Evaluate','Misses + false alarms']].forEach((a,i)=>{let x=xs[i%3],y=ys[Math.floor(i/3)];text(s,a[0],x,y,350,52,34,C.teal,true);box(s,x,y+63,335,2,C.line);text(s,a[1],x,y+86,350,70,27);});
text(s,'The panel reports test metrics after each run',70,619,1090,42,24,C.muted);
}
// 6
{
const s=slide('Cleaning prevents misleading results','0:55','no: counter, not a traffic feature\nDuplicates: remove before split\nHidden label spaces: strip\nLarge numbers: scale\nSame row in train and test: unfairly easy','Notebook Steps 1–3; Colab cleaned counts. Duplicate count = 123117 - 117922. Large numeric scale is documented in the notebook; not a new Colab measurement.');
table(s,[['Problem','Action'],['A row counter called no','Drop it'],['5,195 exact duplicate rows','Remove before splitting'],['Hidden whitespace in labels','Strip label text'],['Features on very different scales','Standardise using training data']],70,180,1140,370,[570,570],29);
text(s,'Clean first, then split',74,596,1110,50,34,C.teal,true);
}
// 7
{
const s=slide('A small MLP learns through a short training loop','1:10','83 raw features; one-hot encoding gives 94 inputs\n64 hidden units; ReLU\nOne output score\nSigmoid inside BCEWithLogitsLoss during training\nDemo: forward; loss; zero gradients; backward; step','Notebook build_mlp and train_model. Colab baseline features=94. PyTorch code in the notebook uses BCEWithLogitsLoss, then sigmoid and threshold 0.5 for evaluation.');
table(s,[['Input','Hidden layer','Output'],['94 values','64 units + ReLU','1 score']],70,180,1140,160,[380,380,380],33);
text(s,'83 original features become 94 numeric inputs after encoding',75,370,1120,56,27,C.muted);
text(s,'forward     loss     zero_grad     backward     step',75,478,1115,64,34,C.teal,true);
text(s,'Batch 256      Adam lr 0.001      At most 30 epochs',75,583,1110,50,28);
}
// 8
{
const s=slide('Adam reaches the lowest loss in this comparison','1:20','Same data; same network; same seed\nThree configurations; different learning rates shown\nMomentum: a rolling ball / 惯性\nAdam: adaptive step per weight\nThis experiment only; not a universal winner');
await pic(s,'optimizers.png',65,140,1150,450);
text(s,'SGD lr 0.1       Momentum lr 0.01       Adam lr 0.001',75,608,1120,48,27,C.muted);
}
// 9
{
const s=slide('The learning rate changes how well Adam learns','1:10','Step size down a hill / 下山步长\n0.00001: slow within 30 epochs\n0.001: lower validation loss\n0.1: unstable here\nSame optimiser; change only learning rate');
await pic(s,'learning-rates.png',65,145,1150,450);
text(s,'Same model and data. Only the learning rate changes.',75,609,1120,47,28,C.teal,true);
}
// 10
{
const o=r.Overfit,e=r['Early stopping'];
const s=slide('Validation shows when more training stops helping','1:20','826 training rows; larger MLP\nTraining loss down; validation loss up\nMock exam / 模拟考\nBest epoch '+o.best_epoch+'; stop after 5 worse checks\nRestore best weights\nMore data is a separate comparison');
await pic(s,'overfitting.png',50,150,865,450);
text(s,'Best epoch',944,200,270,42,25,C.muted);text(s,String(o.best_epoch),944,245,270,76,58,C.teal,true);
text(s,'Early stop at',944,365,270,42,25,C.muted);text(s,String(e.history.val_loss.length),944,412,270,76,58,C.blue,true);
text(s,'1% of training rows. Hidden layers 256 and 128. Adam lr 0.001.',65,612,1140,42,25,C.muted);
}
// 11
{
const s=slide('The baseline catches '+fmt(b['detection rate %'])+'% of attacks','1:00','Read rows: actual traffic\nFalse alarms: '+fmt(b['false alarm rate %'])+'% of normal traffic\nMisses: '+b.confusion[1][0]+' attacks\nThreshold 0.5\nBaseline checkpoint from validation\nOne seed; this dataset; exploratory test result');
await pic(s,'confusion.png',62,145,800,465);
text(s,fmt(b['false alarm rate %'])+'%',900,205,310,85,58,C.red,true);text(s,'false alarms',903,290,310,50,30,C.muted);
text(s,String(b.confusion[1][0]),900,395,310,85,58,C.blue,true);text(s,'missed attacks',903,477,310,50,30,C.muted);
text(s,'Baseline Adam lr 0.001. Test set: 17,689 flows. Threshold: 0.5.',70,622,1130,36,23,C.muted);
}
// 12
{
const s=slide('I learned to check the data and the training process','0:50','My contribution: organised pipeline; training comparisons\nLearned: data first; curves explain failures\nLimits: one seed; binary labels; random split\nTest results visible during experiments\nNext: multiple seeds; fresh evaluation; attack-level recall\nThank you. Notebook demo.','Personal reflection from current experiments. Suggested next steps, not completed work.');
table(s,[['Learned','Limits','Next'],['Training settings change the result','One seed and one random split','Repeat across seeds'],['Validation helps decide when to stop','Only normal / attack labels','Check each attack type'],['The full pipeline must be explainable','Test results visible while exploring','Use a fresh final evaluation']],65,185,1150,335,[384,383,383],26);
text(s,'Thank you. I can show the notebook live.',70,574,1130,65,38,C.teal,true);
}
// Backup 1
{
const s=slide('The demo changes one training setting at a time','Backup','Before talk: Run all\nReset baseline\nTraining: SGD, lr 0.001; Train\nReset baseline\nTraining: Adam, lr 0.001; Train\nIf unavailable: show saved Colab results');
await pic(s,'colab-panel.png',55,150,865,480);
text(s,'1  Run all before the talk\n\n2  SGD, lr 0.001\n\n3  Adam, lr 0.001',942,197,274,330,26);
}
// Backup 2
{
const s=slide('The comparison uses saved Colab runs','Backup','All rows: Adam, SGD, momentum, learning rates\nSmall-data runs: 826 rows, larger network\nBest val is not last val\nPatience 0: last weights\nPatience 5: best weights\nDifferent data/model rows are separate comparisons');
let rows=[['Run','Epochs','Best val','Last val','Detected %','False alarms %']];
for(const [name,v] of Object.entries(r))rows.push([name,String(v.history.val_loss.length),loss(Math.min(...v.history.val_loss)),loss(v.history.val_loss.at(-1)),fmt(v['detection rate %']),fmt(v['false alarm rate %'])]);
table(s,rows,60,155,1160,450,[270,110,180,180,190,230],21);
text(s,'Single seed 42. Settings and full histories accompany the deck.',65,633,1130,35,23,C.muted);
}
// Backup 3
{
const s=slide('Each batch follows five simple steps','Backup','scores: forward pass\nloss: compare scores with labels\nzero_grad: clear previous gradients\nbackward: calculate current gradients\nstep: update weights\nValidation: eval + no_grad\nBest weights: deepcopy; load_state_dict','Exact operations from notebook train_model; shortened formatting for presentation.');
const code='scores = model(X["train"][batch]).squeeze(1)\nloss = loss_fn(scores, y["train"][batch])\noptimizer.zero_grad()\nloss.backward()\noptimizer.step()';
const a=text(s,code,75,193,1130,275,31,C.ink);a.text.style={typeface:'Courier New',fontSize:31,color:C.ink};
text(s,'BCEWithLogitsLoss includes sigmoid during training',75,505,1130,54,29,C.teal,true);
text(s,'Early stopping saves a copy of the best validation weights',75,587,1130,55,27);
}
// Backup 4
{
const s=slide('These sources support the data and methods','Backup','Dataset and three papers checked 18 October 2026','Links shown on slide; checked against publisher, arXiv and UCI pages.');
text(s,'Sharmila, B. S. & Nagapadma, R. (2023)\nQuantized autoencoder (QAE) intrusion detection system for anomaly detection in\nresource-constrained IoT devices using RT-IoT2022 dataset. Cybersecurity 6, 41.\ndoi:10.1186/s42400-023-00178-5',65,153,1160,128,23);
text(s,'Rumelhart, D. E., Hinton, G. E. & Williams, R. J. (1986)\nLearning representations by back-propagating errors. Nature 323, 533–536.\ndoi:10.1038/323533a0',65,305,1160,102,23);
text(s,'Kingma, D. P. & Ba, J. (2015)\nAdam: A Method for Stochastic Optimization. ICLR.\nhttps://arxiv.org/abs/1412.6980',65,433,1160,102,23);
text(s,'RT-IoT2022 dataset, UCI Machine Learning Repository\nhttps://doi.org/10.24432/C5P338',65,564,1160,74,23);
}
await fs.mkdir(path.join(root,'.build/render'),{recursive:true});
for(let i=0;i<pres.slides.items.length;i++){
 const s=pres.slides.items[i];const p=await pres.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(root,'.build/render',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await p.arrayBuffer()));
}
await fs.writeFile(path.join(root,'.build/speaking.json'),JSON.stringify(speaking,null,2));
const candidate=path.join(root,'.build/candidate.pptx');await(await PresentationFile.exportPptx(pres)).save(candidate);
const {finalizePresentation}=await import(path.join(skill,'container_tools/artifact_tool_utils.mjs'));
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:path.join(root,'output/yang-iot-presentation.pptx'),pythonExecutable:runtimePython,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[2,3,6,7,12,14].flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:16,requiredNativeTableOwnerSlides:[2,3,6,7,12,14],fontPolicy:{basis:'design',families:['Arial','Courier New']},verifyArtifactToolImport:true,receiptPath:path.join(root,'.build/validation.json')});
console.log('Created 16 slides: 12 main + 4 backup');
