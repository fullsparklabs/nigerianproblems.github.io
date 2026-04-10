---
layout: default
title: Categories
---

<div class="archive-intro">
  <h1>Problem Categories</h1>
  <p>Browse Nigerian problems by category</p>
</div>

<div class="categories-list">
  {% assign categories = site.categories | sort %}
  
  {% for category in categories %}
    <div class="category-item">
      <h2 id="{{ category[0] }}">
        {{ category[0] | capitalize | replace: '_', ' ' }} 
        <span class="count">({{ category[1].size }} problems)</span>
      </h2>
      <ul>
        {% for post in category[1] limit: 10 %}
          <li>
            <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
            <time datetime="{{ post.date | date_to_xmlschema }}">
              - {{ post.date | date: "%b %d, %Y" }}
            </time>
          </li>
        {% endfor %}
        {% if category[1].size > 10 %}
          <li><a href="{{ site.baseurl }}/categories/{{ category[0] }}">View all {{ category[1].size }} problems →</a></li>
        {% endif %}
      </ul>
    </div>
  {% endfor %}
</div>
