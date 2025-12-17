# designer_code.py

# Hier liegt dein gesamtes Tool als Text-Variable
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matchday Generator</title>
    
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    
    <script src="https://cdn.tailwindcss.com"></script>

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap" rel="stylesheet">

    <style>
        body { font-family: 'Inter', sans-serif; user-select: none; } /* Text markieren verboten */
        /* Custom Scrollbar for Sidebar */
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #1f2937; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #4b5563; border-radius: 20px; }
    </style>
</head>
<body oncontextmenu="return false;">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        // --- ICONS ---
        const IconWrapper = ({ children, className }) => (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
                {children}
            </svg>
        );

        const Upload = ({ className }) => <IconWrapper className={className}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></IconWrapper>;
        const Download = ({ className }) => <IconWrapper className={className}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></IconWrapper>;
        const Palette = ({ className }) => <IconWrapper className={className}><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></IconWrapper>;
        const Type = ({ className }) => <IconWrapper className={className}><polyline points="4 7 4 4 20 4 20 7"/><line x1="9" x2="15" y1="20" y2="20"/><line x1="12" x2="12" y1="4" y2="20"/></IconWrapper>;
        const Shield = ({ className }) => <IconWrapper className={className}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></IconWrapper>;
        const Layout = ({ className }) => <IconWrapper className={className}><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="3" x2="21" y1="9" y2="9"/><line x1="9" x2="9" y1="21" y2="9"/></IconWrapper>;
        const ImageIcon = ({ className }) => <IconWrapper className={className}><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></IconWrapper>;
        const Trash2 = ({ className }) => <IconWrapper className={className}><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></IconWrapper>;
        const Plus = ({ className }) => <IconWrapper className={className}><path d="M5 12h14"/><path d="M12 5v14"/></IconWrapper>;

        // --- MAIN COMPONENT ---
        const MatchdayGenerator = () => {
          const canvasRef = useRef(null);
          
          const [config, setConfig] = useState({
            stripeColor1: '#E63946', 
            stripeColor2: '#1D3557', 
            boxColor: '#000000',     
            boxBorderColor: '#FFFFFF', 
            textColor: '#FFFFFF',    
            textOutlineColor: '#000000', 
            backgroundColor: '#000000', 
            matchTypeSize: 150, 
          });

          const [text, setText] = useState({
            matchType: 'HEIMSPIEL',
            competition: 'Regionalliga Mitte',
            round: '14. Runde',
            homeTeamName: 'Heim Team',
            guestTeamName: 'Gast Team'
          });

          const [images, setImages] = useState({
            mainLogo: null,
            competitionLogo: null,
            homeTeam: null,
            guestTeam: null,
            sponsors: []
          });

          // --- HELPER FUNCTIONS ---
          const handleImageUpload = (e, type) => {
            const file = e.target.files[0];
            if (file) {
              const reader = new FileReader();
              reader.onload = (event) => setImages(prev => ({ ...prev, [type]: event.target.result }));
              reader.readAsDataURL(file);
            }
          };

          const handleSponsorUpload = (e) => {
            const files = Array.from(e.target.files);
            if (files.length === 0) return;
            const remainingSlots = 10 - images.sponsors.length;
            const filesToProcess = files.slice(0, remainingSlots);
            const promises = filesToProcess.map(file => new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.readAsDataURL(file);
              }));
            Promise.all(promises).then(newSponsors => setImages(prev => ({...prev, sponsors: [...prev.sponsors, ...newSponsors]})));
          };

          const removeSponsor = (index) => setImages(prev => ({...prev, sponsors: prev.sponsors.filter((_, i) => i !== index)}));

          const drawScaledImage = (ctx, img, centerX, centerY, maxWidth, maxHeight) => {
            const scale = Math.min(maxWidth / img.width, maxHeight / img.height);
            const w = img.width * scale;
            const h = img.height * scale;
            ctx.drawImage(img, centerX - w / 2, centerY - h / 2, w, h);
          };

          // --- RENDERING LOOP ---
          useEffect(() => {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            const mainLogoImg = new Image();
            const competitionLogoImg = new Image();
            const homeImg = new Image();
            const guestImg = new Image();
            const sponsorImgs = images.sponsors.map(src => { const img = new Image(); img.src = src; return img; });

            const loadImages = () => {
              const promises = [];
              if (images.mainLogo) promises.push(new Promise(resolve => { mainLogoImg.src = images.mainLogo; mainLogoImg.onload = resolve; }));
              if (images.competitionLogo) promises.push(new Promise(resolve => { competitionLogoImg.src = images.competitionLogo; competitionLogoImg.onload = resolve; }));
              if (images.homeTeam) promises.push(new Promise(resolve => { homeImg.src = images.homeTeam; homeImg.onload = resolve; }));
              if (images.guestTeam) promises.push(new Promise(resolve => { guestImg.src = images.guestTeam; guestImg.onload = resolve; }));
              sponsorImgs.forEach(img => promises.push(new Promise(resolve => { img.onload = resolve; })));
              return Promise.all(promises);
            };

            loadImages().then(() => {
              ctx.fillStyle = config.backgroundColor;
              ctx.fillRect(0, 0, 2000, 2000);
              const stripeW = 150;
              ctx.fillStyle = config.stripeColor1;
              ctx.fillRect(0, 0, stripeW, 2000); 
              ctx.fillStyle = config.stripeColor2;
              ctx.fillRect(stripeW, 0, stripeW, 2000); 
              ctx.fillStyle = config.stripeColor2;
              ctx.fillRect(2000 - (stripeW * 2), 0, stripeW, 2000); 
              ctx.fillStyle = config.stripeColor1;
              ctx.fillRect(2000 - stripeW, 0, stripeW, 2000); 

              const drawOutlinedText = (str, x, y, fontSize, color, align = 'right', weight = 'bold') => {
                ctx.textAlign = align;
                ctx.font = `${weight} ${fontSize}px "Inter", sans-serif`;
                ctx.lineJoin = 'round';
                ctx.miterLimit = 2;
                ctx.strokeStyle = config.textOutlineColor;
                ctx.lineWidth = 10;
                ctx.strokeText(str, x, y);
                ctx.fillStyle = color;
                ctx.fillText(str, x, y);
              };

              drawOutlinedText(text.matchType.toUpperCase(), 1900, 75, config.matchTypeSize, config.textColor, 'right', '900');

              if (images.competitionLogo) drawScaledImage(ctx, competitionLogoImg, 1000, 600, 200, 150);
              drawOutlinedText(text.competition, 1000, 730, 60, config.textColor, 'center', 'bold');
              drawOutlinedText(text.round, 1000, 810, 50, config.textColor, 'center', 'normal');

              const boxSize = 400;
              const drawTeamBox = (centerX, centerY, img, teamName) => {
                const x = centerX - (boxSize / 2);
                const y = centerY - (boxSize / 2);
                ctx.fillStyle = config.backgroundColor;
                ctx.fillRect(x, y, boxSize, boxSize);
                if (img && img.src) drawScaledImage(ctx, img, centerX, centerY, 350, 350);
                if (teamName) {
                    const fontSize = 40;
                    const lineHeight = 50;
                    const maxWidth = 500; 
                    const startY = y + boxSize + 60; 
                    ctx.font = `bold ${fontSize}px "Inter", sans-serif`;
                    const words = teamName.split(' ');
                    let line = '';
                    let currentY = startY;
                    for (let n = 0; n < words.length; n++) {
                        const testLine = line + words[n] + ' ';
                        const metrics = ctx.measureText(testLine);
                        if (metrics.width > maxWidth && n > 0) {
                            drawOutlinedText(line, centerX, currentY, fontSize, config.textColor, 'center', 'bold');
                            line = words[n] + ' ';
                            currentY += lineHeight;
                        } else { line = testLine; }
                    }
                    drawOutlinedText(line, centerX, currentY, fontSize, config.textColor, 'center', 'bold');
                }
              };

              drawTeamBox(650, 1100, homeImg, text.homeTeamName);
              drawTeamBox(1350, 1100, guestImg, text.guestTeamName);

              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.font = 'bold 120px "Inter", sans-serif';
              ctx.strokeStyle = config.textOutlineColor;
              ctx.lineWidth = 8;
              ctx.strokeText('VS', 1000, 1100);
              ctx.fillStyle = config.textColor;
              ctx.fillText('VS', 1000, 1100);
              ctx.textBaseline = 'top';

              if (images.mainLogo) {
                ctx.save();
                ctx.shadowColor = "rgba(0,0,0,0.8)";
                ctx.shadowBlur = 25;
                ctx.shadowOffsetX = 5;
                ctx.shadowOffsetY = 5;
                drawScaledImage(ctx, mainLogoImg, 150, 200, 275, 275);
                ctx.restore();
              }

              if (sponsorImgs.length > 0) {
                const gap = 20;
                const maxH = 160;
                const areaYCenter = 1900; 
                const scaledDims = sponsorImgs.map(img => {
                    const ratio = img.width / img.height;
                    return { w: maxH * ratio, h: maxH, img };
                });
                const totalWidth = scaledDims.reduce((acc, item) => acc + item.w, 0) + (gap * (scaledDims.length - 1));
                const availableWidth = 1360; 
                let globalScale = totalWidth > availableWidth ? availableWidth / totalWidth : 1;
                let currentX = 1000 - ((totalWidth * globalScale) / 2);

                scaledDims.forEach(item => {
                    const finalW = item.w * globalScale;
                    const finalH = item.h * globalScale;
                    ctx.drawImage(item.img, currentX, areaYCenter - (finalH / 2), finalW, finalH);
                    currentX += finalW + (gap * globalScale);
                });
              }
            });
          }, [config, text, images]);

          const downloadImage = () => {
            const canvas = canvasRef.current;
            const link = document.createElement('a');
            link.download = `matchday-${text.round.replace(/ /g, '-').toLowerCase()}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
          };

          return (
            <div className="flex flex-col lg:flex-row h-screen bg-gray-900 font-sans overflow-hidden text-gray-100">
              {/* SIDEBAR */}
              <div className="w-full lg:w-[450px] bg-gray-800 border-r border-gray-700 flex flex-col h-full z-20 shadow-xl">
                <div className="p-6 border-b border-gray-700 bg-gray-800">
                  <div className="flex items-center gap-3 mb-1">
                    <div className="p-2 bg-blue-600 rounded-lg"><Layout className="w-5 h-5 text-white" /></div>
                    <h1 className="text-xl font-bold text-white tracking-tight">Matchday Designer</h1>
                  </div>
                  <p className="text-gray-400 text-xs pl-12">Pro Version</p>
                </div>
                <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-gray-400 uppercase tracking-wider">
                      <Type className="w-4 h-4 text-blue-500" />Texte & Status
                    </div>
                    <div className="space-y-3">
                      <div className="group">
                        <label className="block text-xs font-medium text-gray-400 mb-1">Spielstatus</label>
                        <input type="text" value={text.matchType} onChange={(e) => setText({...text, matchType: e.target.value})} className="w-full bg-gray-700 border border-gray-600 text-white text-sm rounded-lg p-2.5 mb-2" />
                        <div className="flex items-center gap-2">
                           <span className="text-xs text-gray-500 whitespace-nowrap">Größe: {config.matchTypeSize}px</span>
                           <input type="range" min="80" max="250" value={config.matchTypeSize} onChange={(e) => setConfig({...config, matchTypeSize: parseInt(e.target.value)})} className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <TextInput label="Liga" value={text.competition} onChange={v => setText({...text, competition: v})} placeholder="Liga" />
                        <TextInput label="Runde" value={text.round} onChange={v => setText({...text, round: v})} placeholder="Runde" />
                      </div>
                      <ImageUpload label="Bewerbslogo" subLabel="Optional" active={!!images.competitionLogo} onChange={(e) => handleImageUpload(e, 'competitionLogo')} />
                    </div>
                  </div>
                  <div className="h-px bg-gray-700" />
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-gray-400 uppercase tracking-wider"><Shield className="w-4 h-4 text-blue-500" />Teams & Logos</div>
                    <div className="grid grid-cols-2 gap-4">
                       <div>
                         <ImageUpload label="Heim" active={!!images.homeTeam} onChange={(e) => handleImageUpload(e, 'homeTeam')} />
                         <input type="text" placeholder="Teamname Heim" value={text.homeTeamName} onChange={(e) => setText({...text, homeTeamName: e.target.value})} className="w-full mt-2 bg-gray-700 border border-gray-600 text-white text-xs rounded p-2" />
                       </div>
                       <div>
                         <ImageUpload label="Gast" active={!!images.guestTeam} onChange={(e) => handleImageUpload(e, 'guestTeam')} />
                         <input type="text" placeholder="Teamname Gast" value={text.guestTeamName} onChange={(e) => setText({...text, guestTeamName: e.target.value})} className="w-full mt-2 bg-gray-700 border border-gray-600 text-white text-xs rounded p-2" />
                       </div>
                    </div>
                    <ImageUpload label="Vereinswappen (Links)" active={!!images.mainLogo} onChange={(e) => handleImageUpload(e, 'mainLogo')} />
                  </div>
                  <div className="h-px bg-gray-700" />
                   <div className="space-y-4">
                    <div className="flex items-center justify-between text-sm font-semibold text-gray-400 uppercase tracking-wider">
                      <div className="flex items-center gap-2"><Shield className="w-4 h-4 text-yellow-500" />Sponsoren (Max 10)</div>
                      <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-white">{images.sponsors.length}/10</span>
                    </div>
                    <div className="grid grid-cols-4 gap-2">
                      {images.sponsors.map((src, idx) => (
                        <div key={idx} className="relative group aspect-square bg-white rounded-lg p-1 flex items-center justify-center overflow-hidden border border-gray-600">
                          <img src={src} alt="sponsor" className="max-w-full max-h-full object-contain" />
                          <button onClick={() => removeSponsor(idx)} className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 className="w-4 h-4 text-red-400" /></button>
                        </div>
                      ))}
                      {images.sponsors.length < 10 && (
                        <label className="aspect-square flex flex-col items-center justify-center border-2 border-dashed border-gray-600 rounded-lg hover:border-yellow-500 hover:bg-yellow-500/10 cursor-pointer transition-colors">
                          <Plus className="w-6 h-6 text-gray-400" /><span className="text-[10px] text-gray-400 mt-1">Add</span><input type="file" className="hidden" accept="image/*" multiple onChange={handleSponsorUpload} />
                        </label>
                      )}
                    </div>
                  </div>
                   <div className="h-px bg-gray-700" />
                   <div className="space-y-4">
                     <div className="flex items-center gap-2 text-sm font-semibold text-gray-400 uppercase tracking-wider"><Palette className="w-4 h-4 text-blue-500" />Farben</div>
                     <div className="grid grid-cols-4 gap-2">
                       <ColorInput mini label="Aussen" value={config.stripeColor1} onChange={v => setConfig({...config, stripeColor1: v})} />
                       <ColorInput mini label="Innen" value={config.stripeColor2} onChange={v => setConfig({...config, stripeColor2: v})} />
                       <ColorInput mini label="Hintergr" value={config.backgroundColor} onChange={v => setConfig({...config, backgroundColor: v})} />
                       <ColorInput mini label="Text" value={config.textColor} onChange={v => setConfig({...config, textColor: v})} />
                     </div>
                   </div>
                </div>
                <div className="p-6 border-t border-gray-700 bg-gray-800">
                  <button onClick={downloadImage} className="w-full group flex items-center justify-center gap-3 px-6 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all duration-200 shadow-lg">
                    <Download className="w-5 h-5" /><span className="font-semibold">Download .PNG</span>
                  </button>
                </div>
              </div>
              {/* MAIN AREA */}
              <div className="flex-1 bg-black relative overflow-hidden flex items-center justify-center p-8 lg:p-12">
                <div className="absolute inset-0 opacity-[0.1]" style={{backgroundImage: `radial-gradient(#333 1px, transparent 1px)`, backgroundSize: '24px 24px'}}></div>
                <div className="relative z-10 max-h-full max-w-full flex flex-col items-center">
                  <div className="bg-black rounded-sm shadow-2xl border border-gray-800 overflow-hidden">
                     <canvas ref={canvasRef} width={2000} height={2000} className="max-w-full max-h-[85vh] h-auto w-auto object-contain" />
                  </div>
                </div>
              </div>
            </div>
          );
        };

        const ColorInput = ({ label, value, onChange }) => (
          <div className="flex flex-col gap-1">
            <div className="relative overflow-hidden w-full aspect-square rounded-md shadow-sm ring-1 ring-white/10 cursor-pointer group">
              <input type="color" value={value} onChange={(e) => onChange(e.target.value)} className="absolute inset-0 w-[150%] h-[150%] -top-[25%] -left-[25%] cursor-pointer p-0 border-0" />
            </div>
            <span className="text-[10px] text-gray-400 text-center truncate">{label}</span>
          </div>
        );

        const TextInput = ({ label, value, onChange, placeholder }) => (
          <div className="group">
            <label className="block text-xs font-medium text-gray-400 mb-1">{label}</label>
            <input type="text" value={value} onChange={(e) => onChange(e.target.value)} className="w-full bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 outline-none placeholder-gray-500" placeholder={placeholder} />
          </div>
        );

        const ImageUpload = ({ label, subLabel, active, onChange }) => (
          <label className={`relative flex flex-col items-center justify-center w-full p-3 border-dashed border rounded-lg cursor-pointer transition-all duration-200 ${active ? 'border-green-500 bg-green-900/20' : 'border-gray-600 bg-gray-700/50 hover:border-blue-500 hover:bg-blue-900/10'}`}>
            {active ? (<div className="flex items-center gap-2 text-green-400"><ImageIcon className="w-4 h-4" /><span className="text-xs font-medium">Geladen</span></div>) : (<div className="flex items-center gap-2 text-gray-400 hover:text-blue-400"><Upload className="w-4 h-4" /><span className="text-xs font-medium">{label}</span></div>)}
            {subLabel && <span className="text-[10px] text-gray-500 mt-1">{subLabel}</span>}
            <input type="file" className="hidden" accept="image/*" onChange={onChange} />
          </label>
        );

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<MatchdayGenerator />);
    </script>
</body>
</html>
"""
