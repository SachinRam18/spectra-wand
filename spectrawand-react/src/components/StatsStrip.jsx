import { useEffect, useRef, useCallback } from 'react';

const STATS = [
    { value: 10, suffix: 'M+', label: 'Images Graded' },
    { value: 340, suffix: '+', label: 'Cinematic Presets' },
    { value: 0.3, suffix: 's', label: 'Avg Process Time' },
    { value: 99.9, suffix: '%', label: 'Uptime SLA' },
];

function animateCount(el, target, suffix, duration = 1600) {
    let start = null;
    const isDecimal = target % 1 !== 0;
    const step = (ts) => {
        if (!start) start = ts;
        const progress = Math.min((ts - start) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const val = isDecimal ? (target * ease).toFixed(1) : Math.floor(target * ease);
        el.textContent = val + suffix;
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

function StatsStrip() {
    const stripRef = useRef(null);
    const sectionRef = useRef(null);
    const counted = useRef(false);

    useEffect(() => {
        const section = sectionRef.current;
        if (!section) return;
        const revObs = new IntersectionObserver(entries => {
            entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view'); });
        }, { threshold: 0.12 });
        revObs.observe(section);
        return () => revObs.disconnect();
    }, []);

    useEffect(() => {
        const el = stripRef.current;
        if (!el) return;
        const obs = new IntersectionObserver(entries => {
            entries.forEach(e => {
                if (e.isIntersecting && !counted.current) {
                    counted.current = true;
                    const nums = el.querySelectorAll('.stat-num');
                    nums.forEach((n, i) => animateCount(n, STATS[i].value, STATS[i].suffix));
                }
            });
        }, { threshold: 0.3 });
        obs.observe(el);
        return () => obs.disconnect();
    }, []);

    return (
        <div className="stats-strip reveal" ref={(el) => { stripRef.current = el; sectionRef.current = el; }}>
            {STATS.map((s, i) => (
                <div className="stat-item" key={i}>
                    <div className="stat-num">0</div>
                    <div className="stat-label">{s.label}</div>
                </div>
            ))}
        </div>
    );
}

export default StatsStrip;
