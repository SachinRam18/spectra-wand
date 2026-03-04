import LOGO from '../assets/logo.png';

function Footer() {
    return (
        <footer className="footer">
            <div className="footer-inner">
                <div className="fsec">
                    <div className="fbrand">
                        <img className="fbrand-mark" src={LOGO} alt="SpectraWand"
                            style={{ width: '40px', height: '40px', borderRadius: '8px' }} />
                        <span className="fbrand-name">SPECTRAWAND</span>
                    </div>
                    <p>Professional AI color grading for photographers, filmmakers, and content creators.</p>
                    <div className="social-row">
                        <a href="#" className="soc"><i className="fa-brands fa-twitter"></i></a>
                        <a href="#" className="soc"><i className="fa-brands fa-instagram"></i></a>
                        <a href="#" className="soc"><i className="fa-brands fa-youtube"></i></a>
                        <a href="#" className="soc"><i className="fa-brands fa-github"></i></a>
                    </div>
                </div>
                <div className="fsec">
                    <h3>Product</h3>
                    <div className="flinks">
                        <a href="#" className="flink">Features</a>
                        <a href="#" className="flink">Pricing</a>
                        <a href="#" className="flink">API</a>
                        <a href="#" className="flink">Integrations</a>
                        <a href="#" className="flink">Changelog</a>
                    </div>
                </div>
                <div className="fsec">
                    <h3>Resources</h3>
                    <div className="flinks">
                        <a href="#" className="flink">Documentation</a>
                        <a href="#" className="flink">Tutorials</a>
                        <a href="#" className="flink">Blog</a>
                        <a href="#" className="flink">Community</a>
                        <a href="#" className="flink">Support</a>
                    </div>
                </div>
                <div className="fsec">
                    <h3>Company</h3>
                    <div className="flinks">
                        <a href="#" className="flink">About</a>
                        <a href="#" className="flink">Careers</a>
                        <a href="#" className="flink">Privacy</a>
                        <a href="#" className="flink">Terms</a>
                        <a href="#" className="flink">Contact</a>
                    </div>
                </div>
            </div>
            <div className="footer-bottom">
                <span className="footer-copy">© 2024 SpectraWand — AI Color Studio</span>
                <div className="footer-spectrum">
                    <div className="specpx" style={{ background: 'var(--c1)' }}></div>
                    <div className="specpx" style={{ background: 'var(--c9)' }}></div>
                    <div className="specpx" style={{ background: 'var(--c6)' }}></div>
                    <div className="specpx" style={{ background: 'var(--c5)' }}></div>
                    <div className="specpx" style={{ background: 'var(--c7)' }}></div>
                    <div className="specpx" style={{ background: 'var(--c4)' }}></div>
                    <div className="specpx" style={{ background: 'var(--c3)' }}></div>
                    <div className="specpx" style={{ background: 'var(--c8)' }}></div>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
