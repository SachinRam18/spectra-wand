import { useState, useEffect, useRef } from 'react';
import BgAmbient from './components/BgAmbient';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import PromptBox from './components/PromptBox';
import Showcase from './components/Showcase';
import StatsStrip from './components/StatsStrip';
import Features from './components/Features';
import Footer from './components/Footer';

function App() {
  const [theme, setTheme] = useState('dark');
  const [uploadedSrc, setUploadedSrc] = useState(null);
  const [gradedSrc, setGradedSrc] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [promptValue, setPromptValue] = useState('');
  const flashRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    // Trigger flash effect
    if (flashRef.current) {
      flashRef.current.classList.remove('active');
      void flashRef.current.offsetWidth; // force reflow
      flashRef.current.classList.add('active');
      setTimeout(() => flashRef.current?.classList.remove('active'), 600);
    }
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setUploadedSrc(ev.target.result);
      setGradedSrc(null);
      setIsProcessing(false);
    };
    reader.readAsDataURL(file);
  };

  const doGrade = () => {
    if (!uploadedSrc) return;
    setIsProcessing(true);
    setGradedSrc(null);
    setTimeout(() => {
      setIsProcessing(false);
      setGradedSrc(uploadedSrc);
    }, 3000);
  };

  const handleTagClick = (tag) => {
    setPromptValue(prev => prev ? prev + ', ' + tag.toLowerCase() : tag.toLowerCase());
  };

  return (
    <>
      <div className="theme-flash" ref={flashRef}></div>
      <BgAmbient />
      <Navbar theme={theme} toggleTheme={toggleTheme} />
      <div className="wrap">
        <Hero />
        <PromptBox
          promptValue={promptValue}
          setPromptValue={setPromptValue}
          onUpload={handleUpload}
          onGrade={doGrade}
          onTagClick={handleTagClick}
        />
        <Showcase
          uploadedSrc={uploadedSrc}
          gradedSrc={gradedSrc}
          isProcessing={isProcessing}
        />
        <StatsStrip />
        <Features />
      </div>
      <Footer />
    </>
  );
}

export default App;
