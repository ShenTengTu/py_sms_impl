module.exports = {
    purge: ["./web/templates/**/*.html"],
    darkMode: false, // or 'media' or 'class'
    theme: {
        extend: {
            lineHeight: {
                0: "0",
                inherit: "inherit",
            },
            borderRadius: {
                circle: "50%",
            },
        },
    },
    variants: {
        extend: {
            ringColor: ["hover"],
        },
    },
    plugins: [],
};
