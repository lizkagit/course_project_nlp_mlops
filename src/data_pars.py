import vk_api
import pandas as pd
import time
import os
from datetime import datetime

def parse_all_posts():
    """
    Парсит ВСЕ посты из групп: текст и количество комментариев
    """
    SERVICE_TOKEN = "52c8762152c8762152c876218f51f4f631552c852c876213bc35b84229b4a487c04dc70"
    
    vk_session = vk_api.VkApi(token=SERVICE_TOKEN)
    vk = vk_session.get_api()
    
    # Группы для парсинга (используй те, что прошли проверку)
    groups = ['mosmetro', 'moscowmetro', 'mirmetro', 'gazetametro']
    
    all_posts = []
    
    print("🚀 НАЧИНАЕМ ПАРСИНГ ВСЕХ ПОСТОВ...")
    
    for group_name in groups:
        try:
            print(f"\n🔍 Парсим группу: {group_name}")
            
            # Сначала получаем общее количество постов
            group_info = vk.groups.getById(group_id=group_name)
            group_data = group_info[0]
            print(f"   📊 Группа: {group_data['name']}")
            
            # Получаем информацию о количестве постов
            test_response = vk.wall.get(domain=group_name, count=1, offset=0)
            total_posts = test_response['count']
            print(f"   📝 Всего постов в группе: {total_posts}")
            
            # Парсим посты пачками по 100
            offset = 0
            batch_size = 100
            group_posts_count = 0
            
            while offset < total_posts:
                response = vk.wall.get(
                    domain=group_name,
                    count=batch_size,
                    offset=offset,
                    filter='all',  # все посты (от группы и другие)
                    extended=0
                )
                
                posts = response['items']
                if not posts:
                    break
                
                for post in posts:
                    # Берем ВСЕ посты с текстом (даже короткие)
                    if post.get('text'):
                        post_data = {
                            'post_id': f"{group_name}_{post['id']}",
                            'group_name': group_name,
                            'group_display_name': group_data['name'],
                            'text': post['text'].strip(),
                            'comments_count': post['comments']['count'],  # КОЛИЧЕСТВО КОММЕНТАРИЕВ
                            'likes': post['likes']['count'],
                            'reposts': post['reposts']['count'],
                            'views': post.get('views', {}).get('count', 0) if 'views' in post else 0,
                            'date': datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S'),
                            'url': f"https://vk.com/{group_name}?w=wall{post['owner_id']}_{post['id']}",
                            'text_length': len(post['text'].strip())
                        }
                        all_posts.append(post_data)
                        group_posts_count += 1
                
                print(f"   📥 Обработано {offset + len(posts)}/{total_posts} постов")
                offset += batch_size
                
                # Пауза чтобы не превысить лимиты API
                time.sleep(0.5)
            
            print(f"✅ Из {group_name} сохранено {group_posts_count} постов")
            
        except Exception as e:
            print(f"❌ Ошибка с группой {group_name}: {e}")
    
    # СОЗДАЕМ ДАТАСЕТ
    df = pd.DataFrame(all_posts)
    
    # Сохраняем данные
    os.makedirs('data/raw', exist_ok=True)
    output_path = 'data/raw/all_posts_v1.csv'
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    # СТАТИСТИКА
    print(f"\n🎉 ПАРСИНГ ЗАВЕРШЕН!")
    print("=" * 60)
    print(f"📊 ФИНАЛЬНАЯ СТАТИСТИКА:")
    print(f"   • Всего постов: {len(df)}")
    print(f"   • Всего комментариев: {df['comments_count'].sum()}")
    print(f"   • Среднее комментариев на пост: {df['comments_count'].mean():.2f}")
    
    print(f"\n🏷️  Статистика по группам:")
    for group in groups:
        group_posts = df[df['group_name'] == group]
        if len(group_posts) > 0:
            print(f"   • {group}: {len(group_posts)} постов, "
                  f"{group_posts['comments_count'].mean():.1f} коммент/пост")
    
    print(f"\n📏 Длина текстов:")
    print(f"   • Средняя длина: {df['text_length'].mean():.1f} символов")
    print(f"   • Минимальная: {df['text_length'].min()} символов")
    print(f"   • Максимальная: {df['text_length'].max()} символов")
    
    print(f"\n📈 Распределение комментариев:")
    ranges = [0, 1, 5, 10, 20, 50, 100, float('inf')]
    range_labels = ['0', '1-5', '6-10', '11-20', '21-50', '51-100', '100+']
    
    for i in range(len(ranges)-1):
        count = len(df[(df['comments_count'] >= ranges[i]) & (df['comments_count'] < ranges[i+1])])
        print(f"   • {range_labels[i]}: {count} постов")
    
    print(f"\n💾 Файл сохранен: {output_path}")
    
    # Примеры постов
    if len(df) > 0:
        print(f"\n📝 ПРИМЕРЫ ПОСТОВ:")
        sample_posts = df.sample(min(5, len(df)))
        for i, (_, post) in enumerate(sample_posts.iterrows(), 1):
            print(f"{i}. [{post['group_name']}]")
            print(f"   Текст: {post['text'][:100]}...")
            print(f"   💬 Комментарии: {post['comments_count']} | "
                  f"❤️ Лайки: {post['likes']} | 📅 {post['date'][:10]}")
            print()
    
    return df

if __name__ == "__main__":
    parse_all_posts()