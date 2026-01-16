# MovieGraphPy - Neo4j Movies Veri Seti ile Python Uygulaması

from neo4j import GraphDatabase
import json
import os
from typing import List, Dict, Optional, Any


class MovieGraphApp:
    def __init__(self, uri: str, user: str, password: str):
        # Neo4j bağlantısını başlatır.
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.selected_movie = None
        
    def close(self):
        # Neo4j bağlantısını kapatır.
        if self.driver:
            self.driver.close()
    
    def test_connection(self) -> bool:
        # Neo4j bağlantısını test eder.
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            print(f"❌ Bağlantı hatası: {e}")
            return False
    
    def search_movies(self, search_term: str) -> List[Dict[str, Any]]:
        # Film adında arama yapar.
        # Args: search_term - Aranacak kelime
        # Returns: Bulunan filmlerin listesi
        if not search_term or not search_term.strip():
            return []
        
        query = """
        MATCH (m:Movie)
        WHERE m.title CONTAINS $search_term
        RETURN m.title AS title, m.released AS released, m.tagline AS tagline
        ORDER BY m.released DESC
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, search_term=search_term.strip())
                movies = []
                for record in result:
                    movies.append({
                        'title': record['title'],
                        'released': record['released'],
                        'tagline': record['tagline']
                    })
                return movies
        except Exception as e:
            print(f"❌ Arama hatası: {e}")
            return []
    
    def get_movie_details(self, movie_title: str) -> Optional[Dict[str, Any]]:
        # Film detaylarını getirir (yönetmenler ve oyuncular dahil).
        # Args: movie_title - Film adı
        # Returns: Film detayları veya None
        query = """
        MATCH (m:Movie {title: $title})
        OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
        OPTIONAL MATCH (a:Person)-[:ACTED_IN]->(m)
        RETURN m.title AS title, 
               m.released AS released, 
               m.tagline AS tagline,
               collect(DISTINCT d.name) AS directors,
               collect(DISTINCT a.name) AS actors
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, title=movie_title)
                record = result.single()
                
                if not record:
                    return None
                
                directors = [d for d in record['directors'] if d is not None]
                actors = [a for a in record['actors'] if a is not None]
                
                return {
                    'title': record['title'],
                    'released': record['released'],
                    'tagline': record['tagline'],
                    'directors': directors,
                    'actors': actors
                }
        except Exception as e:
            print(f"❌ Detay hatası: {e}")
            return None
    
    def generate_graph_json(self, movie_title: str) -> bool:
        # Seçili film için graph.json dosyası oluşturur.
        # Args: movie_title - Film adı
        # Returns: Başarılı olup olmadığı
        query = """
        MATCH (m:Movie {title: $title})
        OPTIONAL MATCH (d:Person)-[r1:DIRECTED]->(m)
        OPTIONAL MATCH (a:Person)-[r2:ACTED_IN]->(m)
        WITH m, 
             collect(DISTINCT {person: d, rel: 'DIRECTED'}) AS director_rels,
             collect(DISTINCT {person: a, rel: 'ACTED_IN'}) AS actor_rels
        RETURN m, director_rels, actor_rels
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, title=movie_title)
                record = result.single()
                
                if not record:
                    return False
                
                # Nodes oluştur
                nodes = []
                node_ids = set()
                
                # Film node'u
                movie_id = f"movie_{record['m']['title'].replace(' ', '_')}"
                nodes.append({
                    'id': movie_id,
                    'label': record['m']['title'],
                    'type': 'Movie',
                    'released': record['m'].get('released'),
                    'tagline': record['m'].get('tagline')
                })
                node_ids.add(movie_id)
                
                # Links oluştur
                links = []
                
                # Yönetmenler
                for dir_rel in record['director_rels']:
                    if dir_rel['person']:
                        person = dir_rel['person']
                        person_id = f"person_{person['name'].replace(' ', '_')}"
                        
                        if person_id not in node_ids:
                            nodes.append({
                                'id': person_id,
                                'label': person['name'],
                                'type': 'Person',
                                'role': 'Director'
                            })
                            node_ids.add(person_id)
                        
                        links.append({
                            'source': person_id,
                            'target': movie_id,
                            'type': 'DIRECTED'
                        })
                
                # Oyuncular
                for act_rel in record['actor_rels']:
                    if act_rel['person']:
                        person = act_rel['person']
                        person_id = f"person_{person['name'].replace(' ', '_')}"
                        
                        if person_id not in node_ids:
                            nodes.append({
                                'id': person_id,
                                'label': person['name'],
                                'type': 'Person',
                                'role': 'Actor'
                            })
                            node_ids.add(person_id)
                        
                        links.append({
                            'source': person_id,
                            'target': movie_id,
                            'type': 'ACTED_IN'
                        })
                
                # JSON oluştur
                graph_data = {
                    'nodes': nodes,
                    'links': links
                }
                
                # exports klasörünü oluştur
                os.makedirs('exports', exist_ok=True)
                
                # JSON dosyasına yaz
                with open('exports/graph.json', 'w', encoding='utf-8') as f:
                    json.dump(graph_data, f, ensure_ascii=False, indent=2)
                
                return True
                
        except Exception as e:
            print(f"❌ Graph oluşturma hatası: {e}")
            return False


def print_menu():
    # Ana menüyü yazdırır.
    print("\n" + "="*50)
    print("🎬 MovieGraphPy - Film Veritabanı Uygulaması")
    print("="*50)
    print("1. Film Ara")
    print("2. Film Detayı Göster")
    print("3. Seçili Film için graph.json Oluştur")
    print("4. Çıkış")
    print("="*50)


def print_movie_list(movies: List[Dict[str, Any]]):
    # Film listesini numaralı olarak yazdırır.
    if not movies:
        print("\n❌ Sonuç bulunamadı.")
        return
    
    print(f"\n📽️  {len(movies)} film bulundu:\n")
    for idx, movie in enumerate(movies, 1):
        year = movie['released'] if movie['released'] else 'Bilinmiyor'
        print(f"{idx}) {movie['title']} ({year})")


def print_movie_details(details: Dict[str, Any]):
    # Film detaylarını yazdırır.
    print("\n" + "="*50)
    print("🎬 Film Detayları")
    print("="*50)
    print(f"📽️  Film: {details['title']}")
    print(f"📅 Yıl: {details['released'] if details['released'] else 'Bilinmiyor'}")
    
    if details['tagline']:
        print(f"💬 Tagline: {details['tagline']}")
    
    print(f"\n🎭 Yönetmen(ler):")
    if details['directors']:
        for director in details['directors']:
            print(f"   • {director}")
    else:
        print("   (Yönetmen bilgisi bulunamadı)")
    
    print(f"\n🎬 Oyuncular:")
    actors = details['actors'][:5] if len(details['actors']) >= 5 else details['actors']
    if actors:
        for actor in actors:
            print(f"   • {actor}")
    else:
        print("   (Oyuncu bilgisi bulunamadı)")
    
    if len(details['actors']) > 5:
        print(f"   ... ve {len(details['actors']) - 5} kişi daha")
    
    print("="*50)


def main():
    # Ana uygulama döngüsü.
    # Neo4j bağlantı bilgileri
    print("🔌 Neo4j bağlantı bilgilerini girin:")
    uri = input("URI (örn: bolt://localhost:7687): ").strip() or "bolt://localhost:7687"
    user = input("Kullanıcı adı (varsayılan: neo4j): ").strip() or "neo4j"
    password = input("Şifre: ").strip()
    
    if not password:
        print("❌ Şifre boş olamaz!")
        return
    
    # Uygulamayı başlat
    app = MovieGraphApp(uri, user, password)
    
    # Bağlantıyı test et
    print("\n🔍 Bağlantı test ediliyor...")
    if not app.test_connection():
        print("❌ Neo4j sunucusuna bağlanılamadı. Lütfen bağlantı bilgilerini kontrol edin.")
        app.close()
        return
    
    print("✅ Bağlantı başarılı!")
    
    # Ana döngü
    last_searched_movies = []
    
    try:
        while True:
            print_menu()
            choice = input("\nSeçiminiz (1-4): ").strip()
            
            if choice == '1':
                # Film Ara
                search_term = input("\n🔍 Aranacak film adı: ").strip()
                
                if not search_term:
                    print("❌ Arama terimi boş olamaz!")
                    continue
                
                movies = app.search_movies(search_term)
                print_movie_list(movies)
                last_searched_movies = movies
                
            elif choice == '2':
                # Film Detayı Göster
                if not last_searched_movies:
                    print("\n❌ Önce film araması yapmalısınız!")
                    continue
                
                try:
                    movie_num = int(input(f"\n📽️  Film numarası seçin (1-{len(last_searched_movies)}): ").strip())
                    
                    if movie_num < 1 or movie_num > len(last_searched_movies):
                        print("❌ Geçersiz numara! Lütfen listeden bir numara seçin.")
                        continue
                    
                    selected_movie = last_searched_movies[movie_num - 1]
                    app.selected_movie = selected_movie
                    
                    details = app.get_movie_details(selected_movie['title'])
                    
                    if details:
                        print_movie_details(details)
                    else:
                        print(f"\n❌ '{selected_movie['title']}' filmi için detay bulunamadı.")
                        
                except ValueError:
                    print("❌ Lütfen geçerli bir numara girin!")
                    continue
                    
            elif choice == '3':
                # Graph.json Oluştur
                if not app.selected_movie:
                    if not last_searched_movies:
                        print("\n❌ Önce bir film seçmelisiniz! (Film Detayı Göster menüsünü kullanın)")
                        continue
                    else:
                        print("\n⚠️  Son aranan filmlerden birini kullanacaksınız.")
                        try:
                            movie_num = int(input(f"Film numarası seçin (1-{len(last_searched_movies)}): ").strip())
                            if movie_num < 1 or movie_num > len(last_searched_movies):
                                print("❌ Geçersiz numara!")
                                continue
                            app.selected_movie = last_searched_movies[movie_num - 1]
                        except ValueError:
                            print("❌ Geçersiz numara!")
                            continue
                
                print(f"\n🔄 '{app.selected_movie['title']}' için graph.json oluşturuluyor...")
                
                if app.generate_graph_json(app.selected_movie['title']):
                    print("✅ graph.json oluşturuldu: exports/graph.json")
                else:
                    print("❌ Graph.json oluşturulamadı. Film bulunamadı veya bir hata oluştu.")
                    
            elif choice == '4':
                # Çıkış
                print("\n👋 Çıkılıyor...")
                break
            else:
                print("\n❌ Geçersiz seçim! Lütfen 1-4 arası bir numara girin.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen bir hata oluştu: {e}")
    finally:
        app.close()


if __name__ == "__main__":
    main()
