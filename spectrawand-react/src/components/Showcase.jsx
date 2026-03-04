import LOGO from '../assets/logo.png';
import { useEffect, useRef } from 'react';

function Showcase({ uploadedSrc, gradedSrc, isProcessing }) {
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

    const hasImage = !!uploadedSrc;

    return (
        <section className="showcase-section reveal" ref={sectionRef}>
            <div className="showcase-wrap">
                <div className="sc-controls">
                    <button className="sc-btn" title="Download"><i className="fa-solid fa-download"></i></button>
                    <button className="sc-btn" title="Share"><i className="fa-solid fa-share-nodes"></i></button>
                    <button className="sc-btn" title="Fullscreen"><i className="fa-solid fa-expand"></i></button>
                </div>
                <div className="sc-label">Image Showcase</div>

                {/* Empty state */}
                {!hasImage && (
                    <div className="empty-state">
                        <div className="empty-prism">
                            <img src={LOGO} width="120" height="120" style={{ borderRadius: '18px' }} alt="SpectraWand" />
                        </div>
                        <h3 className="empty-title">NO GRADES YET</h3>
                        <p className="empty-desc">Upload an image and describe your grade — the before &amp; after will appear here</p>
                    </div>
                )}

                {/* Before / After comparison */}
                {hasImage && (
                    <div className="compare-panel active">
                        {/* LEFT: Original */}
                        <div className="compare-side">
                            <div className="compare-tag">
                                <span className="compare-tag-dot tag-dot-orig"></span>
                                Original
                            </div>
                            <div className="compare-img-wrap">
                                <img src={uploadedSrc} alt="Original" style={{ display: 'block' }} />
                            </div>
                        </div>

                        {/* RIGHT: Graded */}
                        <div className="compare-side">
                            <div className="compare-tag">
                                <span className="compare-tag-dot tag-dot-graded"></span>
                                Graded
                            </div>
                            <div className="compare-img-wrap" style={{ position: 'relative' }}>
                                {gradedSrc && (
                                    <img
                                        src={gradedSrc}
                                        alt="Graded"
                                        style={{
                                            display: 'block',
                                            filter: 'saturate(1.4) contrast(1.1) brightness(0.95) hue-rotate(8deg) sepia(0.12)',
                                            animation: 'fadeIn .5s ease'
                                        }}
                                    />
                                )}
                                {!gradedSrc && !isProcessing && (
                                    <div className="compare-placeholder">
                                        <i className="fa-solid fa-wand-magic-sparkles"></i>
                                        <span>Result appears here</span>
                                    </div>
                                )}
                                {isProcessing && (
                                    <div className="proc active">
                                        <div className="proc-ring-wrap">
                                            <div className="proc-ring"></div>
                                            <div className="proc-dot"></div>
                                        </div>
                                        <p className="proc-txt">Grading your image</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </section>
    );
}

export default Showcase;
