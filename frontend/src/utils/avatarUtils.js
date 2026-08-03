export const getAvatarColors = (seed, theme = 'light') => {
    // Generate consistent hash from seed
    let hash = 0;
    const str = seed || 'user';
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Get hue (0-360)
    const hue = Math.abs(hash % 360);
    
    if (theme === 'dark') {
        // Dark Mode: Background is lighter (like WhatsApp dark mode)
        const bgLightness = 65 + (Math.abs((hash >> 2) % 20)); // 65-85%
        const textLightness = 15 + (Math.abs((hash >> 4) % 15)); // 15-30%
        const saturation = 70 + (Math.abs((hash >> 6) % 25)); // 70-95%
        
        return {
            background: `hsl(${hue}, ${saturation}%, ${bgLightness}%)`,
            text: `hsl(${hue}, ${saturation - 10}%, ${textLightness}%)`,
            hover: `hsl(${hue}, ${saturation}%, ${bgLightness - 10}%)`,
            border: `hsl(${hue}, ${saturation}%, ${bgLightness + 5}%)`
        };
    } else {
        // Light Mode: Background is darker (like WhatsApp light mode)
        const bgLightness = 35 + (Math.abs((hash >> 2) % 20)); // 35-55%
        const textLightness = 85 + (Math.abs((hash >> 4) % 10)); // 85-95%
        const saturation = 75 + (Math.abs((hash >> 6) % 20)); // 75-95%
        
        return {
            background: `hsl(${hue}, ${saturation}%, ${bgLightness}%)`,
            text: `hsl(${hue}, ${saturation - 10}%, ${textLightness}%)`,
            hover: `hsl(${hue}, ${saturation}%, ${bgLightness + 8}%)`,
            border: `hsl(${hue}, ${saturation}%, ${bgLightness - 5}%)`
        };
    }
};

/**
 * Get user initials from first and last name
 * Returns uppercase initials (e.g., "Het Pandya" → "HP")
 */
export const getInitials = (fname, lname) => {
    if (!fname && !lname) return '?';
    const first = fname ? fname.charAt(0).toUpperCase() : '';
    const last = lname ? lname.charAt(0).toUpperCase() : '';
    return first + last;
};

/**
 * Get current theme from localStorage or system preference
 */
export const getCurrentTheme = () => {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) return storedTheme;
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
};