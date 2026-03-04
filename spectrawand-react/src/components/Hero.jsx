function Hero() {
    const swatches = ['sw1', 'sw2', 'sw3', 'sw4', 'sw5', 'sw6', 'sw7', 'sw8'];
    return (
        <section className="hero">
            <div className="hero-eyebrow">AI-Powered Color Grading</div>
            <span className="hero-title-row1">TRANSFORM</span>
            <span className="hero-title-row2">Your Vision</span>
            <span className="hero-sub-mono">with crystalline precision</span>
            <p className="hero-desc">
                Professional AI color grading for photographers, filmmakers, and content creators.
                Achieve cinematic looks in seconds.
            </p>
            <div className="hero-swatches">
                {swatches.map(sw => <div key={sw} className={`swatch ${sw}`}></div>)}
            </div>
        </section>
    );
}

export default Hero;
