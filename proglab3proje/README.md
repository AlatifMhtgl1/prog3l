# MovieGraphPy - Neo4j Movies Veri Seti ile Python Uygulaması

Bu proje, Neo4j Movies demo veri seti ile çalışan bir Python uygulamasıdır. Graf veritabanı kavramlarını öğrenmek ve Cypher sorguları ile veri çekme/güncelleme işlemlerini gerçekleştirmek için tasarlanmıştır.

## Özellikler

- 🎬 Film arama (kısmi arama desteği)
- 📽️ Film detayları görüntüleme (yönetmenler, oyuncular)
- 📊 Graph.json dosyası oluşturma (görselleştirme için)
- 🔒 Hata yönetimi ve validasyon

## Gereksinimler

- Python 3.7+
- Neo4j veritabanı (yerel veya uzak)
- Neo4j Movies demo veri seti

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Neo4j veritabanınızı başlatın ve Movies demo veri setini yükleyin.

3. Uygulamayı çalıştırın:
```bash
python app.py
```

## Kullanım

Uygulama başlatıldığında:

1. Neo4j bağlantı bilgilerini girin:
   - URI (varsayılan: `bolt://localhost:7687`)
   - Kullanıcı adı (varsayılan: `neo4j`)
   - Şifre

2. Ana menüden işlem seçin:
   - **1. Film Ara**: Film adına göre arama yapın
   - **2. Film Detayı Göster**: Seçilen filmin detaylarını görüntüleyin
   - **3. Seçili Film için graph.json Oluştur**: Graf verisini JSON formatında dışa aktarın
   - **4. Çıkış**: Uygulamadan çıkın

## Çıktı Formatı

`graph.json` dosyası şu formatta oluşturulur:

```json
{
  "nodes": [
    {
      "id": "movie_The_Matrix",
      "label": "The Matrix",
      "type": "Movie",
      "released": 1999,
      "tagline": "Welcome to the Real World"
    },
    {
      "id": "person_Keanu_Reeves",
      "label": "Keanu Reeves",
      "type": "Person",
      "role": "Actor"
    }
  ],
  "links": [
    {
      "source": "person_Keanu_Reeves",
      "target": "movie_The_Matrix",
      "type": "ACTED_IN"
    }
  ]
}
```

## Hata Yönetimi

Uygulama aşağıdaki durumları yönetir:
- Boş arama terimi
- Film bulunamadığında uyarı
- Geçersiz numara seçimi
- Neo4j bağlantı hataları

## Notlar

- Film detayı ve graph.json işlemleri, en son aranan ve seçilen film üzerinden yapılır.
- Graph.json dosyası `exports/` klasörüne kaydedilir.
