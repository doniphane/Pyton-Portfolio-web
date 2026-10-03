/* ═══════════════════════════════════════════════════════════════════════════
   Comportements de la page.

   Le site fonctionne sans ce fichier : HTMX se débrouille seul pour les
   fragments projets, et le reste a un rendu serveur complet. Ce qui suit
   n'ajoute que du confort — thème, animation du rôle, suivi de la section
   visible.
   ═══════════════════════════════════════════════════════════════════════════ */

(() => {
  'use strict';

  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ── Thème ────────────────────────────────────────────────────────────── */

  const THEME_KEY = 'theme';

  function applyTheme(theme) {
    root.dataset.theme = theme;
    const label = document.querySelector('[data-theme-label]');
    if (label) {
      label.textContent = theme === 'dark'
        ? 'Passer en thème clair'
        : 'Passer en thème sombre';
    }
  }

  document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      try {
        localStorage.setItem(THEME_KEY, next);
      } catch (error) {
        /* navigation privée : le thème ne sera pas mémorisé */
      }
    });
  });

  // Si l'OS change de thème pendant la visite, on suit — sauf si l'internaute
  // a déjà fait un choix explicite.
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
    let saved = null;
    try {
      saved = localStorage.getItem(THEME_KEY);
    } catch (error) { /* ignoré */ }
    if (!saved) applyTheme(event.matches ? 'dark' : 'light');
  });

  /* ── Rôle cyclé dans le hero ──────────────────────────────────────────── */

  const roleElement = document.querySelector('[data-roles]');
  if (roleElement && !reducedMotion.matches) {
    const roles = (roleElement.dataset.rolesList || '').split('|||').filter(Boolean);
    if (roles.length > 1) {
      let index = 0;
      let deleting = false;
      let text = '';

      const tick = () => {
        const target = roles[index];
        // Le texte ne se réécrit jamais complètement : on garde la frappe.
        if (!deleting && text === target) {
          deleting = true;
          return window.setTimeout(tick, 2600);
        }
        if (deleting && text === '') {
          deleting = false;
          index = (index + 1) % roles.length;
          return window.setTimeout(tick, 320);
        }
        text = deleting ? text.slice(0, -1) : target.slice(0, text.length + 1);
        roleElement.textContent = text;
        window.setTimeout(tick, deleting ? 28 : 62);
      };

      // On démarre sur le rôle déjà présent dans le HTML, puis on enchaîne.
      text = roles[0];
      window.setTimeout(tick, 2600);
    }
  }

  /* ── Section visible dans le rail ─────────────────────────────────────── */

  const railLinks = new Map();
  document.querySelectorAll('[data-rail-link]').forEach((link) => {
    railLinks.set(link.dataset.railLink, link);
  });

  const sections = [...railLinks.keys()]
    .map((id) => document.getElementById(id))
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    const setActive = (id) => {
      railLinks.forEach((link, key) => {
        const active = key === id;
        link.classList.toggle('is-active', active);
        if (active) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    };

    const observer = new IntersectionObserver((entries) => {
      // On retient la section la plus haute encore visible.
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) setActive(visible[0].target.id);
    }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });

    sections.forEach((section) => observer.observe(section));
    setActive(sections[0].id);
  }

  /* ── Modale projet : ouverture, fermeture, carte cliquable ────────────── */

  const modal = document.getElementById('modal-projet');
  if (modal) {
    // Le clic sur la carte (image, texte…) rejoue le clic du titre : c'est lui
    // qui porte le hx-get, donc une seule source de vérité pour l'ouverture.
    document.addEventListener('click', (event) => {
      const card = event.target.closest('.card');
      if (!card) return;
      if (event.target.closest('a, button')) return;
      card.querySelector('[data-project-link]')?.click();
    });

    // Contenu injecté : on ouvre la modale.
    document.addEventListener('htmx:afterSwap', (event) => {
      if (event.detail.target.closest('#modal-projet')) {
        if (!modal.open) modal.showModal();
      }
    });

    modal.querySelector('[data-modal-close]')?.addEventListener('click', () => {
      modal.close();
    });

    // Clic sur le fond (backdrop) : on ferme.
    modal.addEventListener('click', (event) => {
      if (event.target === modal) modal.close();
    });

    // Renvoie le focus sur la carte à la fermeture.
    modal.addEventListener('close', () => {
      const slug = modal.querySelector('[data-slug]')?.dataset.slug;
      if (slug) {
        document.querySelector(`.card__title a[href$="/${slug}"]`)?.focus({ preventScroll: true });
      }
    });
  }

  /* ── Filtres : refléter l'état quand la page est restaurée ────────────── */

  // Le navigateur restaure la page depuis le cache (retour arrière) : les
  // segments peuvent être revenus à leur état d'origine alors que l'URL,
  // elle, a gardé la sélection.
  window.addEventListener('pageshow', (event) => {
    if (!event.persisted) return;
    const params = new URLSearchParams(window.location.search);
    const form = document.getElementById('filtres');
    if (!form) return;

    form.querySelectorAll('button[name]').forEach((button) => {
      const expected = params.get(button.name) || 'all';
      const selected = button.value === expected;
      button.classList.toggle('is-selected', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
  });
})();
