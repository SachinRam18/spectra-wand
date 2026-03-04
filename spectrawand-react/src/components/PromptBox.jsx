import LOGO from '../assets/logo.png';

const TAGS = ['Cinematic', 'Moody', 'Vintage', 'HDR', 'Film Noir', 'Warm Tones'];

function PromptBox({ promptValue, setPromptValue, onUpload, onGrade, onTagClick }) {
    const handleKey = (e) => { if (e.key === 'Enter') onGrade(); };

    return (
        <div className="prompt-wrap">
            <div className="prompt-glow-ring">
                <div className="prompt-card">
                    <div className="prompt-label">
                        <div className="prompt-label-dot"></div>
                        Describe your color grade
                    </div>
                    <div className="prompt-input-row">
                        <div className="prompt-prism-icon">
                            <img src={LOGO} width="28" height="28"
                                style={{ borderRadius: '6px', objectFit: 'cover' }} alt="" />
                        </div>
                        <input
                            className="prompt-field"
                            type="text"
                            placeholder="cinematic sunset, moody noir, warm vintage film…"
                            autoComplete="off"
                            value={promptValue}
                            onChange={e => setPromptValue(e.target.value)}
                            onKeyPress={handleKey}
                        />
                        <div className="prompt-actions">
                            <label className="pa-btn upload" title="Upload image or video">
                                <i className="fa-solid fa-image"></i>
                                <input type="file" accept="image/*,video/*" onChange={onUpload} />
                            </label>
                            <button className="pa-btn send" onClick={onGrade}>
                                <i className="fa-solid fa-wand-magic-sparkles"></i>
                                <span>Generate</span>
                            </button>
                        </div>
                    </div>
                    <div className="prompt-tags-row">
                        {TAGS.map(tag => (
                            <span key={tag} className="ptag" onClick={() => onTagClick(tag)}>{tag}</span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PromptBox;
