/**
 * クッキーに保存
 * @param {string} cookieName 
 * @param {any} obj 
 */
const setCookie = (cookieName, obj) => {
    const jsonString = JSON.stringify(obj);
    const encodedJsonString = encodeURIComponent(jsonString);
    const farFuture = new Date();
    farFuture.setFullYear(farFuture.getFullYear() + 100);
    document.cookie = `${cookieName}=${encodedJsonString}; expires=${farFuture.toUTCString()}; path=/`;
}

/**
 * クッキーから取得
 * @param {string} cookieName 
 * @returns any
 */
const getCookie = (cookieName) => {
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(cookieName + "=")) {
            const encodedJsonString = cookie.substring(cookieName.length + 1);
            const jsonString = decodeURIComponent(encodedJsonString);
            return JSON.parse(jsonString);
        }
    }
    return undefined;
}

/**
 * CSSを動的に読み込む
 */
const loadCssFile = (filePath) => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = filePath;
    document.head.appendChild(link);
}

export { setCookie, getCookie, loadCssFile }
