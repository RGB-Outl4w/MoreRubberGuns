// More Rubber Guns showcase: weapon cards, filters and the EN/RU switch.
// English lives in index.html (works without JS); Russian lives here.

const WEAPONS = [
  {
    id: "mk18", cls: "light", slot: "primary",
    name: { en: "MK18 LL Stinger", ru: "MK18 «Стингер»" },
    type: { en: "Assault rifle", ru: "Штурмовая винтовка" },
    caliber: { en: "5.56x45mm RB", ru: "5,56x45 мм RB" },
    blurb: {
      en: "Simunition-blue MK18 firing low-velocity rubber-tipped rounds.",
      ru: "MK18 в синем учебном исполнении под резиновые патроны пониженной скорости.",
    },
    mag: 30, fire: "auto", rof: "700", vel: "~180", barrel: "262",
    suspect: null, civilian: null,
    att: {
      optics: "Carry-handle irons, SRS, Micro T-2, M5B, HS510C, EXPS3, BOSS Xe, SDR, MRO HD 3x",
      muzzle: "ASR, SFMB, 14\" barrel",
      under: "VFG, AFG, combat grip, RK-1, CQR",
      over: "Laser, PEQ, MAWL",
      light: "M600V",
      mag: "PMAG",
    },
  },
  {
    id: "mp5", cls: "light", slot: "primary",
    name: { en: "MP5 LL Stinger", ru: "MP5 «Стингер»" },
    type: { en: "Submachine gun", ru: "Пистолет-пулемёт" },
    caliber: { en: "9mm P.A. Rubber", ru: "9 мм Р.А." },
    blurb: {
      en: "Simunition-blue MP5A3 feeding 9x22 rubber ball rounds.",
      ru: "MP5A3 в синем учебном исполнении под травматический патрон 9x22.",
    },
    mag: 30, fire: "auto", rof: "800", vel: "~350", barrel: "225",
    suspect: null, civilian: null,
    att: {
      optics: "RMR, SRO, Micro T-2, Aimpro, HS510C, EXPS3, BOSS Xe",
      under: "VFG, AFG, combat grip, RK-1",
      over: "Laser, PEQ",
      light: "Inforce WML",
    },
  },
  {
    id: "lvar", cls: "heavy", slot: "primary",
    name: { en: "LVAR LL Baton", ru: "LVAR «Дубинка»" },
    type: { en: "Assault rifle", ru: "Штурмовая винтовка" },
    caliber: { en: ".300 BLK Baton", ru: ".300 BLK «Дубинка»" },
    blurb: {
      en: "Integrally suppressed, subsonic rubber batons. Suspects shake the stun off fast, so keep firing.",
      ru: "Интегрированный глушитель, дозвуковые резиновые пули. Подозреваемые быстро приходят в себя - продолжайте стрелять.",
    },
    mag: 30, fire: "auto", rof: "750", vel: "~260", barrel: "140",
    suspect: "~5", civilian: 3,
    att: {
      optics: "SRS, Micro T-2, M5B, HS510C, EXPS3, BOSS Xe, SDR, ATACR, MRO HD 3x",
      stock: "Canted irons",
      under: "AFG, combat grip, VFG, RK-1",
      over: "MAWL, laser, PEQ",
      light: "M600V, Inforce WML",
    },
  },
  {
    id: "g19", cls: "light", slot: "secondary",
    name: { en: "G19 LL Stinger", ru: "G19 «Стингер»" },
    type: { en: "Pistol", ru: "Пистолет" },
    caliber: { en: "9mm P.A. Rubber", ru: "9 мм Р.А." },
    blurb: {
      en: "Simunition-blue G19 converted to 9x22 rubber rounds.",
      ru: "G19 в синем учебном исполнении под травматический патрон 9x22.",
    },
    mag: 15, fire: "semi", rof: null, vel: "~330", barrel: "102",
    suspect: null, civilian: null,
    att: {
      optics: "SRO, RMR",
      muzzle: "Compensator",
      under: "Laser, light, IR laser, Steiner PL",
    },
  },
  {
    id: "1911", cls: "heavy", slot: "secondary",
    name: { en: "1911 LL Baton", ru: "1911 «Дубинка»" },
    type: { en: "Pistol", ru: "Пистолет" },
    caliber: { en: ".45 Rubber", ru: ".45 Rubber" },
    blurb: {
      en: "TLE 1911 in less-lethal orange. A beanbag with more punch.",
      ru: "TLE 1911 в оранжевом нелетальном исполнении. Как травматический дробовик, только мощнее.",
    },
    mag: 7, fire: "semi", rof: null, vel: "~220", barrel: "127",
    suspect: "3", civilian: 2, suspectNote: { en: "2 up close", ru: "2 в упор" },
    att: {
      optics: "SRO, RMR",
      muzzle: "Double-port compensator",
      under: "Light, laser",
    },
  },
];

const UI = {
  en: {
    light: "Light", heavy: "Heavy", primary: "Primary", secondary: "Secondary",
    mag: "Magazine", fire: "Fire", rof: "Rate", vel: "Velocity", barrel: "Barrel", effect: "Effect",
    auto: "Semi / Auto", semi: "Semi", rpm: "rpm", ms: "m/s", mm: "mm",
    stun: "Stun", knock: "Knockdown",
    suspect: "Body hits to down a suspect", civilian: "Body hits to down a civilian",
    never: "never: stun only", attachments: "Attachments",
    optics: "Optics", muzzle: "Muzzle", under: "Underbarrel", over: "Overbarrel", stock: "Stock", light_att: "Light", mag_att: "Magazine",
    copied: "Copied",
  },
  ru: {
    light: "Лёгкий", heavy: "Тяжёлый", primary: "Основное", secondary: "Вторичное",
    mag: "Магазин", fire: "Огонь", rof: "Темп", vel: "Скорость", barrel: "Ствол", effect: "Эффект",
    auto: "Одиноч. / Авто", semi: "Одиночный", rpm: "в/мин", ms: "м/с", mm: "мм",
    stun: "Оглушение", knock: "Сбивает",
    suspect: "Попаданий, чтобы свалить подозреваемого", civilian: "Попаданий, чтобы свалить гражданского",
    never: "никогда: только оглушение", attachments: "Обвесы",
    optics: "Прицелы", muzzle: "Дульные", under: "Подствол", over: "Надствол", stock: "Приклад", light_att: "Фонарь", mag_att: "Магазин",
    copied: "Скопировано",
  },
};

const RU = {
  "nav.skip": "К оружию",
  "nav.weapons": "Оружие",
  "nav.play": "Геймплей",
  "nav.install": "Установка",
  "nav.support": "Поддержать",
  "hero.kicker": "Ready or Not · нелетальный мод",
  "hero.lead": "Пять стволов под резиновые пули, чтобы травматический дробовик больше не был единственным нелетальным длинноствольным оружием. Лёгкие стволы оглушают. Тяжёлые сбивают подозреваемых с ног - раненых, но живых.",
  "hero.download": "Скачать .pak",
  "hero.github": "Исходники на GitHub",
  "hero.support": "Поддержать на Boosty",
  "hero.meta1": "2 винтовки · 2 пистолета · 1 ПП",
  "hero.meta2": "Один .pak, загрузчики не нужны",
  "hero.meta3": "Английский и русский",
  "classes.title": "Два вида резины",
  "classes.light.chip": "Лёгкий · Стингер",
  "classes.light.title": "Оглушить, не ранить",
  "classes.light.text": "Каждое попадание оглушает цель, как травматический дробовик, и ломает волю к сопротивлению. Урон символический - 0,1, так что даже полный магазин никого не свалит.",
  "classes.light.who": "MK18 · MP5 · G19 в синем учебном исполнении",
  "classes.heavy.chip": "Тяжёлый · Дубинка",
  "classes.heavy.title": "Свалить, не убить",
  "classes.heavy.text": "Резиновые пули бьют достаточно сильно, чтобы уложить подозреваемого на землю - раненым, но живым. Как и у травматического дробовика, выстрелы в голову и в упор могут убить.",
  "classes.heavy.who": "LVAR · 1911 в оранжевом нелетальном исполнении",
  "arsenal.title": "Арсенал",
  "arsenal.lead": "У каждого ствола модель, анимации и полный список обвесов оригинала (без глушителей), а прицелы правильно выверены.",
  "filter.all": "Все",
  "filter.light": "Лёгкие",
  "filter.heavy": "Тяжёлые",
  "filter.primary": "Основное",
  "filter.secondary": "Вторичное",
  "play.title": "Как это играется",
  "play.light.title": "Лёгкие стволы",
  "play.light.text": "Пара попаданий обычно ставит подозреваемого на колени. Они нужны, чтобы заставить подчиниться, а не чтобы выигрывать перестрелки.",
  "play.pistol.title": "1911 «Дубинка»",
  "play.pistol.text": "Травматический дробовик, только мощнее. Каждое попадание сильно оглушает и сильно бьёт по морали. Если подозреваемый всё равно не подчиняется, 3 попадания в корпус сбивают его с ног (2 в упор).",
  "play.rifle.title": "LVAR «Дубинка»",
  "play.rifle.text": "Создана для плотного огня. Подозреваемые приходят в себя за полсекунды и остаются враждебными, так что сократить дистанцию в 10–20 м не выйдет. Продолжайте стрелять: примерно 5 попаданий в корпус сбивают с ног.",
  "num.suspect": "Здоровье подозреваемого",
  "num.civ": "Здоровье гражданского",
  "num.down": "Сбит с ног при",
  "num.stun": "Оглушение за попадание",
  "num.recover": "LVAR: снова целится через",
  "num.note": "Измерено на стандартной сложности. Тяжёлые попадания наносят +25 в упор, а в голову ×2 и затем +50.",
  "install.title": "Установка за минуту",
  "install.s1.title": "Скачайте",
  "install.s1.text": "Возьмите <code>pakchunk99-Mods_MoreRubberGuns_P.pak</code> из <a href=\"https://github.com/RGB-Outl4w/MoreRubberGuns/releases/latest\">последнего релиза</a>.",
  "install.s2.title": "Положите в игру",
  "install.s2.text": "Скопируйте файл в папку Paks игры:",
  "install.copy": "Копировать",
  "install.s3.title": "Экипируйтесь",
  "install.s3.text": "Запустите игру и откройте экипировку. Стволы во вкладке Less Lethal основного и вторичного слотов.",
  "install.mp": "<b>Мультиплеер:</b> мод нужен каждому игроку в лобби. Чтобы удалить мод, удалите <code>.pak</code>.",
  "install.compat": "<b>Совместимость:</b> собран под Steam-сборку 24942528 (Unreal Engine 5.3). Моды, заменяющие <code>AmmoDataTable</code>, блюпринты прицелов или русский locres движка, будут конфликтовать. <a href=\"https://github.com/RGB-Outl4w/MoreRubberGuns/blob/main/README-ru.md#совместимость\">Подробнее</a>",
  "build.title": "Собран из ваших файлов игры",
  "build.text": "В репозитории нет игровых ассетов. Python-скрипт извлекает ванильное оружие из вашей установки, превращает его в резиновое и упаковывает мод. После патча игры одна команда пересобирает мод под новые файлы.",
  "build.link": "Инструкция по сборке →",
  "support.title": "Нравится мод?",
  "support.text": "More Rubber Guns бесплатный и останется таким. Если он сделал ваши штурмы лучше, можно поддержать разработку на Boosty.",
  "support.btn": "Поддержать на Boosty",
  "footer.license": "Код и сайт: <a href=\"https://github.com/RGB-Outl4w/MoreRubberGuns/blob/main/LICENSE\">MIT</a> © <span class=\"year\">2026</span> OutlawRGB",
  "footer.disclaimer": "Ready or Not и её ассеты принадлежат VOID Interactive. Это бесплатный некоммерческий фанатский мод, не связанный с VOID Interactive и не одобренный ею.",
};

const EN = {};
let lang = "en";
let filter = "all";

function store(key, value) {
  try { value === undefined ? (value = localStorage.getItem(key)) : localStorage.setItem(key, value); } catch { /* storage blocked */ }
  return value;
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}

function pips(n, note) {
  const t = UI[lang];
  if (n === null) return `<span class="pips"><span class="never">${t.never}</span></span>`;
  const count = parseInt(String(n).replace("~", ""), 10);
  const bars = "<i></i>".repeat(count);
  return `<span class="pips" aria-label="${esc(n)}">${bars}<span>&nbsp;${esc(n)}${note ? ` <small>(${esc(note[lang])})</small>` : ""}</span></span>`;
}

function card(w) {
  const t = UI[lang];
  const rows = [
    [t.mag, w.mag],
    [t.fire, t[w.fire]],
    [t.rof, w.rof ? `${w.rof} ${t.rpm}` : "-"],
    [t.vel, `${w.vel} ${t.ms}`],
    [t.barrel, `${w.barrel} ${t.mm}`],
    [t.effect, w.cls === "light" ? t.stun : t.knock],
  ];
  const attLabels = { optics: t.optics, muzzle: t.muzzle, under: t.under, over: t.over, stock: t.stock, light: t.light_att, mag: t.mag_att };
  return `
    <article class="card ${w.cls}" data-cls="${w.cls}" data-slot="${w.slot}">
      <div class="card-top">
        <div class="card-tags">
          <span class="chip ${w.cls}">${t[w.cls]}</span>
          <span class="slot">${t[w.slot]} · ${esc(w.type[lang])}</span>
        </div>
        <h3>${esc(w.name[lang])}</h3>
        <div class="caliber">${esc(w.caliber[lang])}</div>
        <p class="blurb">${esc(w.blurb[lang])}</p>
      </div>
      <dl class="stats">${rows.map(([k, v]) => `<div><dt>${k}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl>
      <div class="knock">
        <div class="knock-row"><span>${t.suspect}</span>${pips(w.suspect, w.suspectNote)}</div>
        <div class="knock-row"><span>${t.civilian}</span>${pips(w.civilian)}</div>
      </div>
      <details>
        <summary>${t.attachments}</summary>
        <dl class="att">${Object.entries(w.att).map(([k, v]) => `<div><dt>${attLabels[k]}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl>
      </details>
    </article>`;
}

function renderCards() {
  const box = document.getElementById("cards");
  box.innerHTML = WEAPONS.map(card).join("");
  applyFilter();
}

function applyFilter() {
  document.querySelectorAll(".card").forEach((el) => {
    el.hidden = !(filter === "all" || el.dataset.cls === filter || el.dataset.slot === filter);
  });
  document.querySelectorAll("[data-filter]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.filter === filter));
}

function setLang(next) {
  lang = next;
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (!(key in EN)) EN[key] = el.textContent;
    el.textContent = lang === "ru" && RU[key] ? RU[key] : EN[key];
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    const key = el.dataset.i18nHtml;
    if (!(key in EN)) EN[key] = el.innerHTML;
    el.innerHTML = lang === "ru" && RU[key] ? RU[key] : EN[key];
  });
  document.querySelectorAll("[data-lang]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.lang === lang));
  document.querySelectorAll(".year").forEach((el) => (el.textContent = new Date().getFullYear()));
  renderCards();
  store("mrg-lang", lang);
}

document.querySelectorAll("[data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));
document.querySelectorAll("[data-filter]").forEach((b) =>
  b.addEventListener("click", () => { filter = b.dataset.filter; applyFilter(); }));
document.querySelectorAll("[data-copy]").forEach((b) =>
  b.addEventListener("click", async () => {
    const text = document.querySelector(b.dataset.copy).textContent;
    try { await navigator.clipboard.writeText(text); } catch { return; }
    const label = b.textContent;
    b.textContent = UI[lang].copied;
    setTimeout(() => (b.textContent = label), 1400);
  }));

const saved = store("mrg-lang");
setLang(saved === "en" || saved === "ru" ? saved
  : (navigator.languages || [navigator.language]).some((l) => /^ru\b/i.test(l || "")) ? "ru" : "en");
