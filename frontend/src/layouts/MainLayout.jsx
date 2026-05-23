import React, {
    useEffect,
    useState
} from "react";

import Navbar from "./Navbar";
import Footer from "./Footer";

function MainLayout({ children }) {

    const [theme, setTheme] = useState(
        () =>
            localStorage.getItem("theme")
            || "light"
    );


    useEffect(() => {

        document.documentElement
            .setAttribute(
                "data-theme",
                theme
            );

        localStorage.setItem(
            "theme",
            theme
        );

    }, [theme]);

    const toggleTheme = () => {

        setTheme(prev =>
            prev === "light"
                ? "dark"
                : "light"
        );
    };

    // =========================
    // LAYOUT
    // =========================

    return (

        <>
            <Navbar
                theme={theme}
                toggleTheme={toggleTheme}
            />

            <main>
                {children}
            </main>

            <Footer theme={theme} />
        </>
    );
}

export default MainLayout;