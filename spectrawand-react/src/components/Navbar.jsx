import LOGO from '../assets/logo.png';

function Navbar({ theme, toggleTheme }) {
    return (
        <nav className="navbar">
            <div className="nav-container">
                <a href="#" className="logo">
                    <img className="prism-mark" src={LOGO} alt="SpectraWand logo"
                        style={{ borderRadius: '12px', width: '95px', height: '95px', objectFit: 'cover' }} />
                    <div className="logo-text-col">
                        <span className="logo-main">SPECTRAWAND</span>
                        <span className="logo-sub">AI Color Studio</span>
                    </div>
                </a>
                <div className="nav-links">
                    <a href="#" className="nav-link">Features</a>
                    <a href="#" className="nav-link">Pricing</a>
                    <a href="#" className="nav-link">Docs</a>
                    <label className="neon-toggle" title="Toggle theme">
                        <input
                            type="checkbox"
                            checked={theme === 'light'}
                            onChange={toggleTheme}
                        />
                        <span className="neon-track">
                            <span className="neon-knob">
                                {theme === 'dark' ? (
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                                        <path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Z" />
                                    </svg>
                                ) : (
                                    <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                                        <circle cx="12" cy="12" r="5" />
                                        <line x1="12" y1="2" x2="12" y2="5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <line x1="12" y1="19" x2="12" y2="22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <line x1="4.93" y1="4.93" x2="6.34" y2="6.34" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <line x1="17.66" y1="17.66" x2="19.07" y2="19.07" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <line x1="2" y1="12" x2="5" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <line x1="19" y1="12" x2="22" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <line x1="4.93" y1="19.07" x2="6.34" y2="17.66" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                        <line x1="17.66" y1="6.34" x2="19.07" y2="4.93" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                    </svg>
                                )}
                            </span>
                        </span>
                    </label>
                    <button className="nav-cta">Get Started</button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
