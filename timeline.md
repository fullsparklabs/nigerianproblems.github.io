---
layout: default
title: Timeline
---

<div class="archive-intro">
  <h1>Timeline of Nigerian Problems</h1>
  <p>Browse problems chronologically from 1960 to present</p>
</div>

<div class="timeline">
  {% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" | sort: "name" | reverse %}
  
  {% for year in posts_by_year %}
    <div class="timeline-year">
      <h2>{{ year.name }}</h2>
      <div class="timeline-items">
        {% for post in year.items %}
          <div class="timeline-item">
            <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
            <time datetime="{{ post.date | date_to_xmlschema }}">
              {{ post.date | date: "%B %d, %Y" }}
            </time>
            {% if post.categories %}
              <div class="categories">
                {% for category in post.categories %}
                  <a href="{{ site.baseurl }}/categories/#{{ category }}">{{ category }}</a>{% unless forloop.last %}, {% endunless %}
                {% endfor %}
              </div>
            {% endif %}
          </div>
        {% endfor %}
      </div>
    </div>
  {% endfor %}
</div>
