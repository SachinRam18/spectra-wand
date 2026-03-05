import { useState, useEffect, useRef } from 'react';
import { gradeImage } from './services/api';
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
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedSrc, setUploadedSrc] = useState(null);
  const [gradedSrc, setGradedSrc] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [promptValue, setPromptValue] = useState('');
  const [errorMsg, setErrorMsg] = useState(null);
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
    setUploadedFile(file);
    setErrorMsg(null);
    const reader = new FileReader();
    reader.onload = (ev) => {
      setUploadedSrc(ev.target.result);
      setGradedSrc(null);
      setIsProcessing(false);
    };
    reader.readAsDataURL(file);
  };

  const doGrade = async () => {
    if (!uploadedFile) {
      alert('Please upload an image first.');
      return;
    }
    if (!promptValue.trim()) {
      alert('Please enter a color grading prompt.');
      return;
    }
    setIsProcessing(true);
    setGradedSrc(null);
    setErrorMsg(null);
    try {
      const data = await gradeImage(uploadedFile, promptValue.trim());
      // Backend returns base64 — convert to data URL
      const mimeType = 'image/jpeg';
      setGradedSrc(`data:${mimeType};base64,${data.image_base64}`);
    } catch (err) {
      console.error('Grading failed:', err);
      setErrorMsg(err.message || 'Something went wrong');
      alert(`Grading failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
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
