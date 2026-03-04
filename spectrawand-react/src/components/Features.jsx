import LOGO from '../assets/logo.png';
import { useEffect, useRef } from 'react';

const FEATURES = [
    { icon: '🎨', title: 'AI-Powered Grading', desc: 'Advanced neural networks analyze and enhance your images with cinematic precision.' },
    { icon: '⚡', title: 'Lightning Fast', desc: 'Process thousands of images in seconds. Batch processing included.' },
    { icon: '🎬', title: 'Cinematic Presets', desc: 'Industry-standard LUTs and presets from Hollywood colorists.' },
    { icon: '📱', title: 'Cross-Platform', desc: 'Works seamlessly on desktop, tablet, and mobile devices.' },
    { icon: '🔒', title: 'Secure & Private', desc: 'Your images are processed securely and never stored on our servers.' },
    { icon: '💎', title: 'Professional Quality', desc: 'Export in RAW, TIFF, or high-quality JPEG with full metadata.' },
    { icon: '🎯', title: 'Smart Automation', desc: 'Intelligent auto-correction and one-click enhancements powered by ML.' },
    { icon: '☁️', title: 'Cloud Sync', desc: 'Access your projects anywhere with automatic cloud synchronization.' },
];

function FeatureCard({ icon, title, desc }) {
    return (
        <div className="fc">
            <div className="fc-inner">
                <div className="fc-glass">
                    <div className="ray"></div>
                    <div className="line topl"></div>
                    <div className="line bottoml"></div>
                    <div className="line leftl"></div>
                    <div className="line rightl"></div>
                    <div className="fc-content">
                        <div className="fc-icon">{icon}</div>
                        <h3 className="fc-title">{title}</h3>
                        <p className="fc-desc">{desc}</p>
                    </div>
                </div>
                <div className="fc-corner">
                    <img src={LOGO} width="32" height="32"
                        style={{ borderRadius: '6px', objectFit: 'cover', opacity: '.85' }} alt="" />
                </div>
            </div>
        </div>
    );
}

function Features() {
    const sectionRef = useRef(null);

    useEffect(() => {
        const el = sectionRef.current;
        if (!el) return;
        const obs = new IntersectionObserver(entries => {
            entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view'); });
        }, { threshold: 0.12 });
        obs.observe(el);
        return () => obs.disconnect();
    }, []);

    return (
        <section className="features-section reveal" ref={sectionRef}>
            <div className="features-header">
                <div className="sec-eyebrow">What We Offer</div>
                <h2 className="sec-title">FEATURES</h2>
                <p className="sec-sub">Everything you need for professional color grading</p>
            </div>
            <div className="features-grid">
                {FEATURES.map((f, i) => (
                    <FeatureCard key={i} {...f} />
                ))}
            </div>
        </section>
    );
}

export default Features;
