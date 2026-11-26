onmessage=async function(event){
 let out='';
 try {
 Sk.configure({__future__:Sk.python3,execLimit:4000,output:s=>{out+=s;if(out.length>16000)throw Error('Output limit reached. Try a smaller loop.');},read:path=>{if(!Sk.builtinFiles.files[path])throw Error('Module unavailable: '+path);return Sk.builtinFiles.files[path];},inputfun:()=>{throw Error('This editor supports programs with values written in the code. Assign a variable instead of calling input().');}});
 await Sk.misceval.asyncToPromise(()=>Sk.importMainWithBody('<stdin>',false,event.data,true));
 postMessage({out});
 }catch(e){postMessage({out,error:e.toString()});}
};
